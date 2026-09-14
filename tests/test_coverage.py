from modules.qmcore.catalog import account_catalog
from modules.qmcore.coverage import build_coverage


def test_account_catalog_prefers_account_scope_over_resource_scope():
    quotas = [
        {'ServiceCode': 'ec2', 'QuotaCode': 'q', 'QuotaAppliedAtLevel': 'RESOURCE', 'QuotaContext': {'ContextId': 'r'}},
        {'ServiceCode': 'ec2', 'QuotaCode': 'q', 'QuotaAppliedAtLevel': 'ACCOUNT', 'Value': 10},
    ]
    selected = account_catalog(quotas)
    assert len(selected) == 1 and selected[0]['QuotaAppliedAtLevel'] == 'ACCOUNT'


def test_coverage_reports_quality_and_scope_breakdown():
    quotas = [
        {'ServiceCode': 'ec2', 'QuotaCode': 'ok', 'QuotaAppliedAtLevel': 'ACCOUNT', 'UsageMetric': {}},
        {'ServiceCode': 'vpc', 'QuotaCode': 'missing', 'QuotaAppliedAtLevel': 'RESOURCE'},
    ]
    entries = [{'serviceCode': 'ec2', 'quotaCode': 'ok', 'qualityStatus': 'OK'}]
    result = build_coverage(quotas, entries)
    assert result['totalCatalog'] == 2
    assert result['accountLevel'] == 1 and result['resourceLevel'] == 1
    assert result['measured'] == 1 and result['ok'] == 1 and result['unsupported'] == 1
    assert result['byReason']['implementation'] == 1
    assert result['byMeasurementType'] == {
        'RESOURCE_COUNT': 1, 'USAGE_METRIC': 0, 'UNSUPPORTED': 1,
        'NO_DATA': 0, 'ERROR': 0}


def test_coverage_counts_documented_metric_missing_from_catalog_metadata():
    quota = {'ServiceCode': 'states', 'QuotaCode': 'L-15D902EC', 'Unit': 'None',
             'QuotaAppliedAtLevel': 'ACCOUNT'}
    result = build_coverage([quota])
    assert result['withUsageMetric'] == 0
    assert result['compatibleUsageMetric'] == 1


def test_coverage_separates_metric_resource_no_data_and_unsupported():
    quotas = [{'ServiceCode': 'svc', 'QuotaCode': code} for code in ('metric', 'resource', 'nodata', 'unsupported')]
    entries = [
        {'serviceCode': 'svc', 'quotaCode': 'metric', 'qualityStatus': 'OK', 'dataSource': 'official_metric'},
        {'serviceCode': 'svc', 'quotaCode': 'resource', 'qualityStatus': 'OK', 'dataSource': 'resource_check'},
        {'serviceCode': 'svc', 'quotaCode': 'nodata', 'qualityStatus': 'NO_DATA', 'dataSource': 'resource_check'},
    ]
    result = build_coverage(quotas, entries)
    assert result['byMeasurementType'] == {
        'RESOURCE_COUNT': 1, 'USAGE_METRIC': 1, 'UNSUPPORTED': 1,
        'NO_DATA': 1, 'ERROR': 0}


def test_coverage_groups_operational_and_no_data_reasons():
    quotas = [
        {'ServiceCode': 'ec2', 'QuotaCode': 'no-data'},
        {'ServiceCode': 'ec2', 'QuotaCode': 'error'},
    ]
    entries = [
        {'serviceCode': 'ec2', 'quotaCode': 'no-data', 'qualityStatus': 'NO_DATA',
         'qualityReason': 'Missing, invalid or zero limit'},
        {'serviceCode': 'ec2', 'quotaCode': 'error', 'qualityStatus': 'ERROR',
         'qualityReason': 'Throttling while listing resources'},
    ]
    result = build_coverage(quotas, entries)
    assert result['noDataByReason']['invalid_limit'] == 1
    assert result['errorByReason']['throttling'] == 1
