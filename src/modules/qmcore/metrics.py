"""Resolve exact quota metrics and reduce every CloudWatch page over fixed intervals."""
from datetime import timedelta
from modules.qmcore.aws import Unsupported
from modules.qmcore.model import measurement, number, iso, utcnow

# CloudWatch units are filters, not conversions. Unit=None in Service Quotas
# is supported only for known count metrics whose dimensionality is documented.
CW_UNITS = {'Count', 'Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes', 'Terabytes',
            'Seconds', 'Milliseconds', 'Microseconds', 'Percent', 'Bits',
            'Kilobits', 'Megabits', 'Gigabits', 'Terabits', 'Count/Second',
            'Bytes/Second', 'Bits/Second', 'Kilobytes/Second', 'Megabytes/Second',
            'Gigabytes/Second', 'Terabytes/Second', 'Kilobits/Second',
            'Megabits/Second', 'Gigabits/Second', 'Terabits/Second'}

# Service Quotas does not attach UsageMetric metadata to every metric that AWS
# documents specifically for a quota. Keep these account/Region mappings
# explicit rather than guessing from quota names.
DOCUMENTED_USAGE_METRICS = {
    ('states', 'L-B8A5B662'): {
        'MetricNamespace': 'AWS/States',
        'MetricName': 'OpenExecutionCount',
        'MetricDimensions': {},
        'MetricStatisticRecommendation': 'Maximum',
    },
    ('states', 'L-15D902EC'): {
        'MetricNamespace': 'AWS/States',
        'MetricName': 'ApproximateOpenMapRunCount',
        'MetricDimensions': {},
        'MetricStatisticRecommendation': 'Maximum',
    },
}


def normalize_usage_metric(quota):
    """Extract and validate the CloudWatch identity from a catalog quota.

    The returned structure is deterministic and contains only fields used by
    CloudWatch. Invalid, unresolved, or ambiguous catalog definitions raise
    ``Unsupported`` so coverage records them instead of guessing a metric.
    """
    key = (quota.get('ServiceCode'), quota.get('QuotaCode'))
    metric = quota.get('UsageMetric') or DOCUMENTED_USAGE_METRICS.get(key, {})
    namespace, name = metric.get('MetricNamespace'), metric.get('MetricName')
    dims = metric.get('MetricDimensions', {})
    if not isinstance(dims, dict):
        raise Unsupported('Metric dimensions are not an object')
    if not namespace or not isinstance(namespace, str) or not name or not isinstance(name, str):
        raise Unsupported('Metric identity contains missing or invalid namespace/name')
    if any(not isinstance(k, str) or not k or not isinstance(v, str) or not v
           or any(c in v for c in '*${}') for k, v in dims.items()):
        raise Unsupported('Metric identity contains missing or unresolved dimensions')
    stat = metric.get('MetricStatisticRecommendation')
    if stat not in {'Maximum', 'Sum'}:
        raise Unsupported('Missing or unsupported statistic recommendation')
    return {'Namespace': namespace, 'MetricName': name,
            'Dimensions': [{'Name': k, 'Value': dims[k]} for k in sorted(dims)],
            'Statistic': stat}


def metric_spec(quota, period=60):
    if quota.get('GlobalQuota') or quota.get('QuotaAppliedAtLevel') == 'RESOURCE':
        raise Unsupported('Global or resource-specific quota needs explicit scope resolution')
    normalized = normalize_usage_metric(quota)
    namespace, name = normalized['Namespace'], normalized['MetricName']
    dims, stat = normalized['Dimensions'], normalized['Statistic']
    unit = quota.get('Unit')
    if unit in {None, 'None'}:
        if (namespace == 'AWS/Usage' and name in {'ResourceCount', 'CallCount'}) or (
                namespace == 'AWS/Lambda' and name in {'ConcurrentExecutions', 'UnreservedConcurrentExecutions'}) or (
                namespace == 'AWS/States' and name in {'OpenExecutionCount', 'ApproximateOpenMapRunCount'}):
            unit = 'Count'
        else:
            raise Unsupported('Metric and quota units cannot be established')
    if unit not in CW_UNITS:
        raise Unsupported(f'Unsupported quota unit: {unit}')
    divisor = 1
    if stat == 'Sum':
        # A Sum only has quota semantics over a specified rate window.
        rate = quota.get('Period') or {}
        scale = {'SECOND': 1, 'MINUTE': 60, 'HOUR': 3600, 'DAY': 86400}.get(rate.get('PeriodUnit'))
        value = number(rate.get('PeriodValue'))
        if not scale or not value:
            raise Unsupported('Sum metric without an explicit quota rate window')
        window = int(scale * value)
        if window < 60 or window % 60 or period > window:
            raise Unsupported('CloudWatch resolution cannot reproduce quota rate window')
        period = window
        # Values are counts in the quota period; no unverified per-second averaging.
    spec = {'Metric': {'Namespace': namespace, 'MetricName': name,
                       'Dimensions': dims},
            'Period': period, 'Stat': stat, 'Unit': unit}
    return spec, unit, divisor


def compatible(quota):
    try:
        metric_spec(quota)
        return True
    except Unsupported:
        return False


def fetch_metrics(ctx, quotas, start, end, historical=False):
    if start >= end:
        raise ValueError('Metric interval must have start < end')
    age = utcnow() - start
    period = (3600 if age > timedelta(days=63) else 300 if age > timedelta(days=15) else 60) if historical else 60
    results, ready = [], []
    for quota in quotas:
        if quota.get('ErrorReason'):
            results.append(_entry(ctx, quota, None, 'ERROR', str(quota['ErrorReason']), start, end, period))
            continue
        try:
            spec, unit, divisor = metric_spec(quota, period)
            ready.append((quota, spec, unit, divisor))
        except Unsupported as exc:
            results.append(_entry(ctx, quota, None, 'UNSUPPORTED', str(exc), start, end, period))
    for offset in range(0, len(ready), 500):
        batch = ready[offset:offset + 500]
        queries = [{'Id': f'm{i}', 'MetricStat': spec, 'ReturnData': True}
                   for i, (_, spec, _, _) in enumerate(batch)]
        maxima, timestamps, counts, errors, seen_ids = {}, {}, {}, {}, set()
        next_token, seen_tokens, pending = None, set(), set()
        try:
            while True:
                kwargs = dict(MetricDataQueries=queries, StartTime=start, EndTime=end)
                if next_token:
                    kwargs['NextToken'] = next_token
                response = ctx.client('cloudwatch').get_metric_data(**kwargs)
                if response.get('Messages'):
                    raise RuntimeError(f"CloudWatch: {response['Messages']}")
                for result in response.get('MetricDataResults', []):
                    index = int(result['Id'][1:])
                    seen_ids.add(index)
                    status = result.get('StatusCode')
                    if status == 'PartialData' and response.get('NextToken'):
                        pending.add(index)
                    elif status == 'Complete':
                        pending.discard(index)
                    else:
                        errors[index] = f'Incomplete metric result: {status}'
                    if result.get('Messages'):
                        errors[index] = f"Metric messages: {result['Messages']}"
                    values, times = result.get('Values', []), result.get('Timestamps', [])
                    if len(values) != len(times):
                        errors[index] = 'Metric timestamps and values differ in length'
                    for value, timestamp in zip(values, times):
                        if not start <= timestamp < end:
                            continue
                        value = number(value)
                        if value is None:
                            errors[index] = 'Invalid metric value'
                            continue
                        counts[index] = counts.get(index, 0) + 1
                        if index not in maxima or value > maxima[index]:
                            maxima[index], timestamps[index] = value, timestamp
                next_token = response.get('NextToken')
                if not next_token:
                    break
                if next_token in seen_tokens:
                    raise RuntimeError('Repeated CloudWatch pagination token')
                seen_tokens.add(next_token)
        except Exception as exc:
            errors.update({i: str(exc) for i in range(len(batch))})
        for index in pending:
            errors[index] = 'CloudWatch pagination did not complete this query'
        for i, (quota, spec, unit, divisor) in enumerate(batch):
            if i not in seen_ids and i not in errors:
                errors[i] = 'CloudWatch omitted requested query'
            entry = _entry(ctx, quota, maxima.get(i), 'ERROR' if i in errors else 'OK',
                           errors.get(i, ''), start, end, spec['Period'], unit)
            entry['peakAt'] = iso(timestamps[i]) if i in timestamps else None
            entry['sampleCount'] = counts.get(i, 0)
            entry['metricStatistic'] = spec['Stat']
            results.append(entry)
    return results


def _entry(ctx, quota, usage, status, reason, start, end, period, unit=None):
    result = measurement(ctx.account, ctx.region, quota['ServiceCode'], quota['QuotaCode'],
                         quota.get('QuotaName', quota['QuotaCode']), quota.get('Value'), usage,
                         now=ctx.now, status=status, reason=reason,
                         unit=unit or quota.get('Unit', 'Count'), source='official_metric', method='CLOUDWATCH_MAX')
    result.update(windowStart=iso(start), windowEnd=iso(end), aggregationSeconds=period)
    return result
