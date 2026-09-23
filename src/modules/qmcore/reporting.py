"""UTC reporting with exclusive endpoints, scoped history and explicit quality."""
import csv
import os
from datetime import datetime, timedelta, UTC
from io import StringIO
from itertools import pairwise
from modules.qmcore.model import iso, utcnow, valid_measurement, number
from modules.qmcore.metrics import compatible, fetch_metrics
from modules.qmcore.catalog import account_catalog
from modules.qmcore.registry import custom_keys

CUSTOM_KEYS = custom_keys()


def report_period(event=None, now=None):
    event, now = event or {}, now or utcnow()
    mode = event.get('period')
    scheduled = event.get('source') in {'eventbridge-scheduler', 'aws.events'}
    if mode not in {None, 'previous_month', 'rolling'}:
        raise ValueError('period must be previous_month or rolling')
    if mode == 'previous_month' or scheduled:
        if 'days_back' in event:
            raise ValueError('days_back is incompatible with a calendar-month report')
        # Use the scheduled event time so delayed retries keep the same month.
        if scheduled and event.get('time'):
            now = datetime.fromisoformat(event['time'].replace('Z', '+00:00'))
            if now.tzinfo is None:
                raise ValueError('Event time must include a timezone')
        end = now.astimezone(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (end - timedelta(days=1)).replace(day=1)
    else:
        raw = event.get('days_back', os.getenv('QM_REPORT_DAYS', '30'))
        try:
            if isinstance(raw, bool) or str(raw) != str(int(raw)):
                raise ValueError('days_back must be an integer')
            days = int(raw)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('days_back must be an integer') from exc
        if not 1 <= days <= 455:
            raise ValueError('days_back must be between 1 and 455')
        end = now.astimezone(UTC).replace(microsecond=0)
        start = end - timedelta(days=days)
    return start, end


def iter_history(db, account, region, start, end):
    kwargs = {
        'FilterExpression': 'begins_with(PK, :prefix) AND #sk >= :start AND #sk < :end AND accountId = :account AND #region = :region',
        'ExpressionAttributeNames': {'#sk': 'SK', '#region': 'region'},
        'ExpressionAttributeValues': {':prefix': 'QUOTA#', ':start': 'TS#' + iso(start), ':end': 'TS#' + iso(end),
                                      ':account': account, ':region': region},
        'ConsistentRead': True,
    }
    while True:
        response = db.table.scan(**kwargs)
        yield from response.get('Items', [])
        if not response.get('LastEvaluatedKey'):
            return
        kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']


def load_history(db, account, region, start, end):
    """Convenience API for small callers; reporting uses the streaming iterator."""
    return list(iter_history(db, account, region, start, end))


def empty_group():
    return {'latest': None, 'excluded': 0, 'errors': 0, 'statuses': set(),
            'customPeak': None, 'customCount': 0, 'customUnits': set(), 'times': set(), 'peakLimits': set()}


def aggregate_history(items, start, end, metric_peaks=None):
    groups = {}
    metric_peaks = metric_peaks or {}
    for item in items:
        key = (item['accountId'], item['region'], item['serviceCode'], item['quotaCode'])
        group = groups.setdefault(key, empty_group())
        if not group['latest'] or item['collectedAt'] > group['latest']['collectedAt']:
            group['latest'] = item
        group['statuses'].add(item.get('qualityStatus'))
        if not valid_measurement(item):
            group['excluded'] += 1
            group['errors'] += item.get('qualityStatus') == 'ERROR'
            continue
        if item.get('dataSource') == 'official_metric':
            peak = metric_peaks.get(key[2:])
            if peak and item.get('peakAt') == peak.get('peakAt') and item['unit'] == peak['unit']:
                group['peakLimits'].add(item['limitValue'])
        else:
            group['customCount'] += 1
            group['customUnits'].add(item['unit'])
            group['times'].add(item['collectedAt'])
            if not group['customPeak'] or item['usageValue'] > group['customPeak']['usageValue']:
                group['customPeak'] = item
    return groups


def _coverage(times, start, end):
    times = sorted(datetime.fromisoformat(t.replace('Z', '+00:00')) for t in times)
    if not times:
        return False
    edges = [start, *times, end]
    return all(b - a <= timedelta(minutes=30) for a, b in pairwise(edges))


def build_report(ctx, db, quotas, start, end):
    errors = []
    scan_failed = False
    catalog = {(q['ServiceCode'], q['QuotaCode']): q for q in account_catalog(quotas)}
    selected_metrics = [q for key, q in catalog.items() if compatible(q) or
                        (q.get('UsageMetric') and key not in CUSTOM_KEYS)]
    cw = {(e['serviceCode'], e['quotaCode']): e for e in fetch_metrics(ctx, selected_metrics, start, end, historical=True)}
    try:
        history = aggregate_history(iter_history(db, ctx.account, ctx.region, start, end), start, end, cw)
    except Exception as exc:
        history = {}
        scan_failed = True
        errors.append(f'History scan incomplete: {exc}')
    # Preserve visibility of old/custom quotas even when no longer in the current catalog.
    for account, region, service, code in history:
        if account == ctx.account and region == ctx.region:
            item = history[(account, region, service, code)]['latest']
            catalog.setdefault((service, code), dict(ServiceCode=service, QuotaCode=code,
                QuotaName=item.get('quotaName', code), Unit=item.get('unit'), Value=None))
    rows = []
    for key, q in sorted(catalog.items()):
        group = history.get((ctx.account, ctx.region, *key), empty_group())
        row = dict(accountId=ctx.account, region=ctx.region, serviceCode=key[0], quotaCode=key[1],
                   quotaName=q.get('QuotaName', key[1]), currentLimit=q.get('Value'), limitAtPeak=None,
                   maxUsage=None, peakAt=None, unit=q.get('Unit'), usageSource='not_supported',
                   measurementType='UNSUPPORTED',
                   qualityStatus='UNSUPPORTED', qualityReason='No compatible usage metric or resource check',
                   periodStart=iso(start), periodEnd=iso(end), excludedSamples=group['excluded'],
                   sampleCount=0, aggregationSeconds=None, calculationVersion=2)
        if key in cw:
            entry = cw[key]
            row.update(maxUsage=entry['usageValue'], peakAt=entry.get('peakAt'), unit=entry['unit'],
                       usageSource='official_metric', measurementType='USAGE_METRIC', qualityStatus=entry['qualityStatus'],
                       qualityReason=entry['qualityReason'], sampleCount=entry.get('sampleCount', 0),
                       aggregationSeconds=entry.get('aggregationSeconds'))
            limits = group['peakLimits']
            if len(limits) == 1:
                row['limitAtPeak'] = next(iter(limits))
        elif key in CUSTOM_KEYS or group['latest']:
            row.update(usageSource='resource_check', measurementType='RESOURCE_COUNT',
                       qualityStatus='NO_DATA', qualityReason='No verified samples in period')
            peak = group['customPeak']
            units = group['customUnits']
            if len(units) > 1:
                row.update(qualityStatus='ERROR', qualityReason='Incompatible historical units')
            elif peak:
                row.update(maxUsage=peak['usageValue'], limitAtPeak=peak['limitValue'], peakAt=peak['collectedAt'],
                           unit=peak['unit'], sampleCount=group['customCount'], qualityStatus='OK', qualityReason='')
                if row['unit'] != q.get('Unit') and q.get('Unit') not in {None, 'None'}:
                    scale = {'Kilobytes': 1024, 'Megabytes': 1024**2, 'Gigabytes': 1024**3}.get(q.get('Unit'))
                    if row['unit'] == 'Bytes' and scale and number(q.get('Value')) is not None:
                        row['currentLimit'] = number(q['Value']) * scale
                    else:
                        row.update(currentLimit=None, qualityStatus='ERROR', qualityReason='Current/historical limit units differ')
                if row['qualityStatus'] == 'OK' and not _coverage(group['times'], start, end):
                    row.update(qualityStatus='NO_DATA', qualityReason='Partial history: collection gaps exceed 30 minutes')
            elif group['statuses'] == {'UNSUPPORTED'}:
                row.update(qualityStatus='UNSUPPORTED', qualityReason=group['latest'].get('qualityReason', 'Unsupported check'))
            if group['excluded'] and row['qualityStatus'] == 'OK':
                row.update(qualityStatus='NO_DATA', qualityReason='Partial history: invalid or legacy samples excluded')
            if group['errors'] or scan_failed:
                row.update(qualityStatus='ERROR', qualityReason='Partial history: collector or history scan errors')
        if row['qualityStatus'] == 'ERROR':
            errors.append(f"{key[0]}/{key[1]}: {row['qualityReason']}")
        rows.append(row)
    return rows, errors


COLUMNS = {'Period Start (UTC)': 'periodStart', 'Period End Exclusive (UTC)': 'periodEnd',
           'Account': 'accountId', 'Region': 'region', 'Service': 'serviceCode',
           'Quota Code': 'quotaCode', 'Quota Name': 'quotaName', 'Current Limit': 'currentLimit',
           'Limit at Usage Peak': 'limitAtPeak', 'Max Usage in Period': 'maxUsage', 'Peak At (UTC)': 'peakAt',
           'Unit': 'unit', 'Measurement Type': 'measurementType', 'Usage Source': 'usageSource',
           'Data Quality': 'qualityStatus',
           'Quality Detail': 'qualityReason', 'Samples': 'sampleCount', 'Excluded Samples': 'excludedSamples',
           'Aggregation Seconds': 'aggregationSeconds', 'Calculation Version': 'calculationVersion',
           'Report Status': 'reportStatus'}


def generate_csv_report(rows):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(COLUMNS))
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(field) for column, field in COLUMNS.items()})
    return output.getvalue()
