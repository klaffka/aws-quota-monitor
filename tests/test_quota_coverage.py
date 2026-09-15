import json
import pytest

from scripts.quota_coverage import (catalog_coverage, compare_baseline, load_catalog,
                                    merge_catalogs, render_table, totals,
                                    unmeasurable)


def test_catalog_coverage_deduplicates_scopes_and_reports_uncovered():
    quotas = [
        {'serviceCode': 'AWSCloudMap', 'quotaCode': 'implemented'},
        {'serviceCode': 'AWSCloudMap', 'quotaCode': 'implemented', 'scope': 'account'},
        {'serviceCode': 'servicediscovery', 'quotaCode': 'uncovered'},
    ]
    rows = catalog_coverage(quotas, {('servicediscovery', 'implemented')})
    assert rows == [{'serviceCode': 'servicediscovery', 'total': 2, 'implemented': 1,
                     'compatibleMetric': 0, 'covered': 1, 'coveredPct': 50.0,
                     'uncovered': 1, 'uncoveredCodes': ['uncovered'], 'implementedPct': 50.0,
                     'unmeasurable': 0, 'measurable': 2, 'measurablePct': 50.0}]


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


def write(tmp_path, name, quotas):
    path = tmp_path / name
    path.write_text(json.dumps(quotas), encoding='utf-8')
    return str(path)


def test_merged_catalogs_union_entries_and_prefer_the_later_export(tmp_path):
    first = write(tmp_path, 'old.json', [{'serviceCode': 'example', 'quotaCode': 'one'},
                                         {'serviceCode': 'example', 'quotaCode': 'both'}])
    second = write(tmp_path, 'new.json', [metric_quota('both'), metric_quota('two')])
    merged = merge_catalogs([first, second])
    assert {(q['ServiceCode'], q['QuotaCode']) for q in merged} == {
        ('example', 'one'), ('example', 'both'), ('example', 'two')}
    row, = catalog_coverage(merged, set())
    # The later export carries the usage metadata that makes 'both' compatible.
    assert (row['total'], row['compatibleMetric']) == (3, 2)


def test_baseline_reports_every_measure_that_regressed(tmp_path):
    rows = catalog_coverage([metric_quota('one'), {'ServiceCode': 'example',
                                                   'QuotaCode': 'two'}], set())
    assert totals(rows) == {'total': 2, 'implemented': 0, 'compatibleMetric': 1,
                            'covered': 1, 'uncovered': 1, 'unmeasurable': 0,
                            'measurable': 2}
    baseline = tmp_path / 'baseline.json'
    baseline.write_text(json.dumps({'covered': 1, 'implemented': 0}), encoding='utf-8')
    assert compare_baseline(rows, str(baseline)) == []
    baseline.write_text(json.dumps({'covered': 2, 'compatibleMetric': 3}), encoding='utf-8')
    assert compare_baseline(rows, str(baseline)) == ['compatibleMetric fell from 3 to 1',
                                                     'covered fell from 2 to 1']


def named(code, name):
    return {'ServiceCode': 'example', 'QuotaCode': code, 'QuotaName': name}


def test_token_bucket_rate_and_burst_quotas_are_classified_as_unmeasurable():
    quotas = [named('bucket', 'DescribeThings request bucket maximum capacity'),
              named('refill', 'DescribeThings request bucket refill rate'),
              named('tps', 'DescribeActivations TPS'),
              named('burst', 'CreateCase burst quota'),
              named('countable', 'Cases per domain')]
    row, = catalog_coverage(quotas, set())
    assert (row['total'], row['unmeasurable'], row['measurable']) == (5, 4, 1)
    # Coverage against the measurable base is the honest denominator.
    assert (row['coveredPct'], row['measurablePct']) == (0.0, 0.0)


def test_published_burst_throughput_metrics_stay_measurable():
    # EFS bursting throughput is a CloudWatch metric, not a request bucket.
    row, = catalog_coverage([named('efs', 'Bursting throughput')], set())
    assert row['unmeasurable'] == 0


def test_a_covered_quota_is_never_counted_as_unmeasurable():
    quotas = [named('tps', 'DescribeActivations TPS')]
    row, = catalog_coverage(quotas, {('example', 'tps')})
    assert (row['covered'], row['unmeasurable'], row['measurablePct']) == (1, 0, 100.0)


def test_the_table_reports_both_denominators():
    rows = catalog_coverage([named('tps', 'DescribeActivations TPS'),
                             named('countable', 'Cases per domain')],
                            {('example', 'countable')})
    table = render_table(rows)
    assert 'Unmeas' in table and 'OfMeasurable' in table
    # One of two quotas covered, but one of one measurable quota.
    assert '50.0%' in table and '100.0%' in table


def test_baseline_also_fails_when_more_quotas_are_excluded(tmp_path):
    rows = catalog_coverage([named('tps', 'DescribeActivations TPS')], set())
    baseline = tmp_path / 'baseline.json'
    baseline.write_text(json.dumps({'unmeasurable': 0}), encoding='utf-8')
    assert compare_baseline(rows, str(baseline)) == ['unmeasurable grew from 0 to 1']
    baseline.write_text(json.dumps({'unmeasurable': 1}), encoding='utf-8')
    assert compare_baseline(rows, str(baseline)) == []


def test_per_second_rates_are_excluded_whatever_the_wording():
    quotas = [named('a', 'TPS limit for CreateDestination'),
              named('b', 'DescribeThings throttle limit in transactions per second'),
              named('c', 'ListOpsItemEvents requests per second'),
              named('d', 'Messages Published per Second'),
              named('e', 'Policy generations per day'),
              named('f', 'Rate of DescribeAcmeEndpoint API requests')]
    row, = catalog_coverage(quotas, set())
    # Rates with a stated per-second window are excluded; a daily rate and an
    # unqualified request rate stay in the measurable base.
    assert (row['unmeasurable'], row['measurable']) == (4, 2)


def test_an_official_metric_beats_the_rate_rule():
    quota = metric_quota('tps')
    quota['QuotaName'] = 'Transactions per second (TPS) for the GetPatchBaseline API'
    row, = catalog_coverage([quota], set())
    assert (row['covered'], row['unmeasurable']) == (1, 0)


def test_throttle_rates_are_excluded_like_other_per_second_limits():
    quotas = [named('a', 'StartJobRun API throttle rate quota'),
              named('b', 'Throttle rate limit for CreateAutomationRule'),
              named('c', 'Throttle rate (ListAlerts)'),
              named('d', 'Ingestion rate per workspace')]
    row, = catalog_coverage(quotas, set())
    # An unqualified ingestion rate keeps no stated window, so it stays measurable.
    assert (row['unmeasurable'], row['measurable']) == (3, 1)


def test_operation_throttle_limits_are_excluded_but_named_counts_are_not():
    quotas = [named('a', 'ListDevices throttle limit'),
              named('b', 'CreateAdapter throttle limit for max number of adapters '
                         'per account'),
              named('c', 'Async DocumentAnalysis throttle limit for max number of '
                         'concurrent jobs')]
    row, = catalog_coverage(quotas, set())
    # Only the bare "<Operation> throttle limit" wording names a rate.
    assert (row['unmeasurable'], row['measurable']) == (1, 2)


def test_rate_quotas_are_excluded_alongside_their_burst_twin():
    quotas = [named('rate', 'CreateCase rate quota'),
              named('burst', 'CreateCase burst quota'),
              named('count', 'Cases per domain')]
    row, = catalog_coverage(quotas, set())
    assert (row['unmeasurable'], row['measurable']) == (2, 1)


def test_every_catalog_rate_quota_has_an_excluded_burst_twin():
    """The rate rule rests on that pairing, so a lone rate quota must fail here."""
    import re
    catalog = load_catalog('tests/fixtures/quota-catalog-union.json')
    names = {}
    for quota in catalog:
        names.setdefault(quota['ServiceCode'], {})[quota.get('QuotaName') or ''] = quota
    unpaired = []
    for service, entries in names.items():
        for name in entries:
            if not re.search(r'rate quota$', name, re.I):
                continue
            twin = re.sub(r'rate quota$', 'burst quota', name, flags=re.I)
            if unmeasurable(entries.get(twin, {})) != 'API_BURST':
                unpaired.append((service, name))
    assert not unpaired, f'rate quotas without a burst twin: {unpaired[:5]}'


def test_the_progress_document_reports_the_measured_union_totals():
    """The union column is reproducible, so the document must not drift from it."""
    import re
    from pathlib import Path
    measured = totals(catalog_coverage(
        load_catalog('tests/fixtures/quota-catalog-union.json')))
    document = Path('docs/quota-coverage-progress.md').read_text(encoding='utf-8')
    for measure in ('total', 'implemented', 'compatibleMetric', 'covered',
                    'uncovered', 'unmeasurable', 'measurable'):
        row = re.search(rf'^\| {measure} \| ([\d,]+) \|', document, re.MULTILINE)
        assert row, f'{measure} is missing from the progress table'
        assert int(row.group(1).replace(',', '')) == measured[measure], measure
    share = re.search(r'\*\*([\d.]+)%\*\* of the whole union', document)
    assert share and float(share.group(1)) == round(
        measured['covered'] / measured['total'] * 100, 2)
    measurable = re.search(r'\*\*([\d.]+)%\*\* of the ([\d,]+) quotas', document)
    assert measurable and float(measurable.group(1)) == round(
        measured['covered'] / measured['measurable'] * 100, 2)
    assert int(measurable.group(2).replace(',', '')) == measured['measurable']
