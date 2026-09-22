"""Validated measurements. Unknown values are never numeric zero."""
import math
from datetime import datetime, UTC

CALCULATION_VERSION = 2
STATUSES = {'OK', 'NO_DATA', 'UNSUPPORTED', 'ERROR'}


def utcnow():
    return datetime.now(UTC)


def iso(value):
    return value.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def measurement(account, region, service, code, name, limit=None, usage=None,
                *, now=None, unit='Count', status='OK', reason='', source='resource_check',
                resource_type=None, resource_id=None, meta=None, method='REGION_TOTAL'):
    now = now or utcnow()
    limit, usage = number(limit), number(usage)
    if status not in STATUSES:
        raise ValueError('Unknown quality status')
    if status == 'OK' and (limit is None or limit == 0):
        status, reason = 'NO_DATA', 'Missing, invalid or zero limit'
    if status == 'OK' and usage is None:
        status, reason = 'NO_DATA', 'Missing or invalid usage'
    if status in {'ERROR', 'UNSUPPORTED'}:
        usage = None
    return {
        'PK': f'QUOTA#{account}#{region}#quota#{code}', 'SK': f'TS#{iso(now)}',
        'accountId': account, 'region': region, 'serviceCode': service,
        'quotaCode': code, 'quotaName': name, 'scopeType': 'ACCOUNT_REGION',
        'limitValue': limit, 'usageValue': usage,
        'utilizationPct': round(usage / limit * 100, 4) if status == 'OK' else None,
        'unit': unit, 'qualityStatus': status, 'qualityReason': reason,
        'calculationVersion': CALCULATION_VERSION, 'collectorType': method,
        'dataSource': source, 'calculationMethod': method,
        'maxResourceType': resource_type, 'maxResourceId': resource_id,
        'maxResourceMeta': meta, 'collectedAt': iso(now),
        'ttl': int(now.timestamp()) + 64 * 86400,
    }


def valid_measurement(item):
    usage, limit = number(item.get('usageValue')), number(item.get('limitValue'))
    return (item.get('qualityStatus') == 'OK'
            and item.get('calculationVersion') == CALCULATION_VERSION
            and usage is not None and limit is not None and limit > 0
            and bool(item.get('unit')))
