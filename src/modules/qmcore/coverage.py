"""Coverage summaries used to track which catalog quotas are measurable."""


def reason_group(reason):
    text = str(reason or 'unknown').lower()
    if 'no measurement implementation' in text or 'no compatible usage metric' in text:
        return 'implementation'
    if 'throttl' in text:
        return 'throttling'
    if 'accessdenied' in text or 'access denied' in text or 'permission' in text:
        return 'permission'
    if 'pagination' in text or 'partial' in text:
        return 'pagination'
    if 'limit' in text and ('invalid' in text or 'zero' in text or 'missing' in text):
        return 'invalid_limit'
    if 'api' in text or 'clienterror' in text:
        return 'api'
    if 'scope' in text or 'dimension' in text:
        return 'scope'
    if 'statistic' in text:
        return 'statistic'
    if 'unit' in text:
        return 'unit'
    if 'access' in text:
        return 'permission'
    if 'metric' in text:
        return 'metric'
    if 'no data' in text or 'sample' in text:
        return 'no_data'
    return 'other'


def build_coverage(quotas, entries=()):
    """Return a JSON/DynamoDB-safe snapshot of catalog measurement coverage."""
    from modules.qmcore.metrics import compatible
    quotas = list(quotas or ())
    entries = list(entries or ())
    by_key = {(e.get('serviceCode'), e.get('quotaCode')): e for e in entries}
    summary = {
        'totalCatalog': len(quotas),
        'accountLevel': sum(q.get('QuotaAppliedAtLevel', 'ACCOUNT') == 'ACCOUNT' for q in quotas),
        'resourceLevel': sum(q.get('QuotaAppliedAtLevel') == 'RESOURCE' for q in quotas),
        'globalLevel': sum(q.get('QuotaAppliedAtLevel') == 'GLOBAL' for q in quotas),
        'withUsageMetric': sum(bool(q.get('UsageMetric')) for q in quotas),
        'compatibleUsageMetric': sum(compatible(q) for q in quotas),
        'unsupportedMetric': 0,
        'measured': 0,
        'ok': 0,
        'noData': 0,
        'errors': 0,
        'unsupported': 0,
        'byService': {},
        'byReason': {},
        'noDataByReason': {},
        'errorByReason': {},
        'byMeasurementType': {'RESOURCE_COUNT': 0, 'USAGE_METRIC': 0,
                              'UNSUPPORTED': 0, 'NO_DATA': 0, 'ERROR': 0},
    }
    for quota in quotas:
        key = (quota.get('ServiceCode'), quota.get('QuotaCode'))
        entry = by_key.get(key)
        service = quota.get('ServiceCode') or 'unknown'
        bucket = summary['byService'].setdefault(service, {
            'catalog': 0, 'measured': 0, 'unsupported': 0, 'noData': 0,
            'errors': 0, 'resourceCount': 0, 'usageMetric': 0})
        bucket['catalog'] += 1
        status = entry.get('qualityStatus') if entry else 'UNSUPPORTED'
        if status == 'NO_DATA':
            measurement_type = 'NO_DATA'
        elif status == 'ERROR':
            measurement_type = 'ERROR'
        elif status == 'UNSUPPORTED' or not entry:
            measurement_type = 'UNSUPPORTED'
        elif entry.get('dataSource') == 'official_metric':
            measurement_type = 'USAGE_METRIC'
        else:
            measurement_type = 'RESOURCE_COUNT'
        summary['byMeasurementType'][measurement_type] += 1
        if measurement_type == 'RESOURCE_COUNT':
            bucket['resourceCount'] += 1
        elif measurement_type == 'USAGE_METRIC':
            bucket['usageMetric'] += 1
        if entry:
            summary['measured'] += 1
            bucket['measured'] += 1
        if status == 'OK':
            summary['ok'] += 1
        elif status == 'NO_DATA':
            summary['noData'] += 1
            bucket['noData'] += 1
            reason = reason_group(entry.get('qualityReason') if entry else 'No data')
            summary['noDataByReason'][reason] = summary['noDataByReason'].get(reason, 0) + 1
        elif status == 'ERROR':
            summary['errors'] += 1
            bucket['errors'] += 1
            reason = reason_group(entry.get('qualityReason') if entry else 'Unknown error')
            summary['errorByReason'][reason] = summary['errorByReason'].get(reason, 0) + 1
        else:
            summary['unsupported'] += 1
            bucket['unsupported'] += 1
            reason = reason_group(entry.get('qualityReason') if entry else 'No measurement implementation')
            summary['byReason'][reason] = summary['byReason'].get(reason, 0) + 1
        if quota.get('UsageMetric') and not entry:
            summary['unsupportedMetric'] += 1
    return summary
