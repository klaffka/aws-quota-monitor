import json
import pytest

from scripts.quota_coverage import catalog_coverage, load_catalog, render_table


def test_catalog_coverage_deduplicates_scopes_and_reports_uncovered():
    quotas = [
        {'serviceCode': 'AWSCloudMap', 'quotaCode': 'implemented'},
        {'serviceCode': 'AWSCloudMap', 'quotaCode': 'implemented', 'scope': 'account'},
        {'serviceCode': 'servicediscovery', 'quotaCode': 'uncovered'},
    ]
    rows = catalog_coverage(quotas, {('servicediscovery', 'implemented')})
    assert rows == [{'serviceCode': 'servicediscovery', 'total': 2, 'implemented': 1,
                     'compatibleMetric': 0, 'covered': 1, 'coveredPct': 50.0,
                     'uncovered': 1, 'uncoveredCodes': ['uncovered'], 'implementedPct': 50.0}]


def test_catalog_loader_accepts_quotas_wrapper_and_table(tmp_path):
    path = tmp_path / 'catalog.json'
    path.write_text(json.dumps({'Quotas': [{'serviceCode': 'x', 'quotaCode': 'q'}]}), encoding='utf-8')
    rows = catalog_coverage(load_catalog(str(path)), set())
    assert '50.0%' not in render_table(rows)
    assert rows[0]['implementedPct'] == 0.0


def metric_quota(code, **fields):
    return dict(ServiceCode='example', QuotaCode=code, Unit='None', UsageMetric={
        'MetricNamespace': 'AWS/Usage', 'MetricName': 'ResourceCount',
        'MetricDimensions': {'Service': 'Example', 'Resource': code},
        'MetricStatisticRecommendation': 'Maximum'}, **fields)


def test_native_catalog_counts_union_of_custom_and_compatible_metrics():
    quotas = [metric_quota('both'), metric_quota('metric'),
              {'ServiceCode': 'example', 'QuotaCode': 'custom'},
              metric_quota('global', GlobalQuota=True),
              metric_quota('resource', QuotaAppliedAtLevel='RESOURCE')]
    row, = catalog_coverage(quotas, {('example', 'both'), ('example', 'custom')})
    assert (row['total'], row['implemented'], row['compatibleMetric'], row['covered']) == (5, 2, 2, 3)
    assert row['uncoveredCodes'] == ['global', 'resource']
    assert row['coveredPct'] == 60.0
    assert 'TOTAL' in render_table([row])


def test_native_account_scope_wins_over_resource_scope_regardless_of_order():
    account = metric_quota('shared', QuotaAppliedAtLevel='ACCOUNT')
    resource = metric_quota('shared', QuotaAppliedAtLevel='RESOURCE')
    for quotas in ([account, resource], [resource, account]):
        row, = catalog_coverage(quotas, set())
        assert row['total'] == row['covered'] == 1


def test_malformed_catalog_entries_fail_instead_of_disappearing():
    with pytest.raises(ValueError, match='ServiceCode/QuotaCode'):
        catalog_coverage([{'ServiceCode': 'example'}], set())


def test_legacy_metric_export_is_normalized():
    quota = {key[0].lower() + key[1:]: value for key, value in metric_quota('q').items()}
    row, = catalog_coverage([quota], set())
    assert row['compatibleMetric'] == row['covered'] == 1


def test_sum_without_exact_rate_window_stays_uncovered():
    quota = metric_quota('api-rate')
    quota['UsageMetric']['MetricName'] = 'CallCount'
    quota['UsageMetric']['MetricStatisticRecommendation'] = 'Sum'
    row, = catalog_coverage([quota], set())
    assert row['uncoveredCodes'] == ['api-rate']


def test_documented_metric_without_catalog_usage_metadata_is_covered():
    quota = {'ServiceCode': 'states', 'QuotaCode': 'L-B8A5B662', 'Unit': 'None',
             'QuotaAppliedAtLevel': 'ACCOUNT'}
    row, = catalog_coverage([quota], set())
    assert row['compatibleMetric'] == row['covered'] == 1
