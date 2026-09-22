from datetime import datetime, timedelta, UTC
from unittest.mock import Mock
import boto3
import pytest
from botocore.stub import Stubber
from modules.qmcore.aws import CheckContext, Unsupported
from modules.qmcore.metrics import fetch_metrics, metric_spec, normalize_usage_metric


def test_usage_metric_normalization_is_deterministic():
    quota = {'UsageMetric': {'MetricNamespace': 'AWS/Usage', 'MetricName': 'ResourceCount',
                             'MetricDimensions': {'Z': 'z', 'A': 'a'},
                             'MetricStatisticRecommendation': 'Maximum'}}
    assert normalize_usage_metric(quota)['Dimensions'] == [
        {'Name': 'A', 'Value': 'a'}, {'Name': 'Z', 'Value': 'z'}]


def test_usage_metric_normalization_rejects_ambiguous_dimensions():
    quota = {'UsageMetric': {'MetricNamespace': 'AWS/Usage', 'MetricName': 'ResourceCount',
                             'MetricDimensions': ['bad'],
                             'MetricStatisticRecommendation': 'Maximum'}}
    with pytest.raises(Unsupported):
        normalize_usage_metric(quota)


@pytest.mark.parametrize('code,name', [
    ('L-B8A5B662', 'OpenExecutionCount'),
    ('L-15D902EC', 'ApproximateOpenMapRunCount'),
])
def test_documented_stepfunctions_quota_metrics_fill_missing_catalog_metadata(code, name):
    q = {'ServiceCode': 'states', 'QuotaCode': code, 'QuotaName': name,
         'QuotaAppliedAtLevel': 'ACCOUNT', 'Unit': 'None', 'Value': 1000}
    normalized = normalize_usage_metric(q)
    assert normalized == {
        'Namespace': 'AWS/States', 'MetricName': name, 'Dimensions': [], 'Statistic': 'Maximum'}
    spec, unit, divisor = metric_spec(q)
    assert spec['Metric'] == {'Namespace': 'AWS/States', 'MetricName': name, 'Dimensions': []}
    assert spec['Stat'] == 'Maximum' and unit == 'Count' and divisor == 1


def test_metric_query_preserves_dimensions_statistic_and_unit():
    client = Mock()
    client.get_metric_data.return_value = {
        'MetricDataResults': [
            {'Id': 'm0', 'StatusCode': 'Complete', 'Values': [3, 11, 7],
             'Timestamps': [NOW - timedelta(minutes=3), NOW - timedelta(minutes=2),
                            NOW - timedelta(minutes=1)]}
        ]
    }
    q = quota()
    q['Unit'] = 'Bytes'
    q['UsageMetric']['MetricDimensions'] = {'Region': 'eu-central-1', 'Service': 'EC2'}
    entry, = fetch_metrics(ctx_for(client), [q], NOW - timedelta(minutes=20), NOW)
    query = client.get_metric_data.call_args.kwargs['MetricDataQueries'][0]['MetricStat']
    assert query['Stat'] == 'Maximum' and query['Unit'] == 'Bytes'
    assert query['Metric']['Dimensions'] == [
        {'Name': 'Region', 'Value': 'eu-central-1'}, {'Name': 'Service', 'Value': 'EC2'}]
    assert entry['usageValue'] == 11 and entry['sampleCount'] == 3

NOW = datetime.now(UTC).replace(second=0, microsecond=0)


def quota(code='q'):
    return dict(ServiceCode='ec2', QuotaCode=code, QuotaName='quota', Unit='None', Value=100,
                UsageMetric=dict(MetricNamespace='AWS/Usage', MetricName='ResourceCount',
                                 MetricDimensions={'Service': 'EC2'}, MetricStatisticRecommendation='Maximum'))


def ctx_for(client):
    session = Mock(region_name='eu-central-1')
    session.client.return_value = client
    return CheckContext(session, account='a', now=NOW)


def response(values, times, **kwargs):
    return dict(MetricDataResults=[dict(Id='m0', StatusCode='Complete', Values=values, Timestamps=times)], **kwargs)


def test_all_cloudwatch_pages_reduce_maximum_with_stubber():
    client = boto3.client('cloudwatch')
    with Stubber(client) as stub:
        stub.add_response('get_metric_data', response([90], [NOW-timedelta(minutes=2)], NextToken='page2'))
        stub.add_response('get_metric_data', response([20], [NOW-timedelta(minutes=1)]))
        entry, = fetch_metrics(ctx_for(client), [quota()], NOW-timedelta(minutes=20), NOW)
        assert entry['usageValue'] == 90
        assert entry['utilizationPct'] == 90
        assert entry['qualityStatus'] == 'OK'
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('kind,expected', [('empty', 'NO_DATA'), ('partial', 'ERROR'), ('denied', 'ERROR'), ('throttle', 'ERROR')])
def test_missing_and_errors(kind, expected):
    client = Mock()
    if kind in {'denied', 'throttle'}:
        client.get_metric_data.side_effect = RuntimeError('AccessDenied' if kind == 'denied' else 'Throttling')
    else:
        client.get_metric_data.return_value = response([], [])
        if kind == 'partial':
            client.get_metric_data.return_value['MetricDataResults'][0]['StatusCode'] = 'PartialData'
    entry, = fetch_metrics(ctx_for(client), [quota()], NOW-timedelta(minutes=20), NOW)
    assert entry['qualityStatus'] == expected
    assert entry['utilizationPct'] is None


def test_pagination_failure_discards_partial_max():
    client = Mock()
    client.get_metric_data.side_effect = [response([90], [NOW-timedelta(minutes=1)], NextToken='next'), RuntimeError('Throttling')]
    entry, = fetch_metrics(ctx_for(client), [quota()], NOW-timedelta(minutes=20), NOW)
    assert entry['qualityStatus'] == 'ERROR'
    assert entry['usageValue'] is None


def test_statistic_resolution_and_unit_validation():
    q = quota()
    q['UsageMetric']['MetricStatisticRecommendation'] = 'Sum'
    with pytest.raises(Unsupported):
        metric_spec(q)
    q['Period'] = {'PeriodUnit': 'MINUTE', 'PeriodValue': 1}
    spec, unit, _ = metric_spec(q)
    assert spec['Stat'] == 'Sum' and spec['Period'] == 60 and unit == 'Count'
    with pytest.raises(Unsupported):
        metric_spec(q, period=300)
    q = quota()
    q['UsageMetric']['MetricDimensions']['Resource'] = '${ResourceId}'
    with pytest.raises(Unsupported):
        metric_spec(q)
    q = quota()
    q['Unit'] = 'Widgets'
    with pytest.raises(Unsupported):
        metric_spec(q)


def test_batching_and_fixed_historical_period():
    client = Mock()
    client.get_metric_data.return_value = response([], [])
    fetch_metrics(ctx_for(client), [quota(str(i)) for i in range(501)], NOW-timedelta(days=30), NOW, historical=True)
    assert client.get_metric_data.call_count == 2
    calls = client.get_metric_data.call_args_list
    assert len(calls[0].kwargs['MetricDataQueries']) == 500
    assert calls[0].kwargs['MetricDataQueries'][0]['MetricStat']['Period'] == 300
    assert calls[1].kwargs['StartTime'] == calls[0].kwargs['StartTime']


def test_exclusive_end_and_zero_are_distinct_from_missing():
    client = Mock()
    client.get_metric_data.return_value = response([900, 0], [NOW, NOW-timedelta(minutes=1)])
    entry, = fetch_metrics(ctx_for(client), [quota()], NOW-timedelta(minutes=20), NOW)
    assert entry['qualityStatus'] == 'OK' and entry['usageValue'] == 0


def test_partial_pagination_is_ok_only_when_query_finishes():
    client = Mock()
    partial = response([90], [NOW-timedelta(minutes=2)], NextToken='next')
    partial['MetricDataResults'][0]['StatusCode'] = 'PartialData'
    client.get_metric_data.side_effect = [partial, response([20], [NOW-timedelta(minutes=1)])]
    result, = fetch_metrics(ctx_for(client), [quota()], NOW-timedelta(minutes=20), NOW)
    assert result['qualityStatus'] == 'OK' and result['usageValue'] == 90


def test_metric_with_unknown_or_global_scope_is_not_queried():
    client = Mock()
    q = quota()
    q['GlobalQuota'] = True
    result, = fetch_metrics(ctx_for(client), [q], NOW-timedelta(minutes=20), NOW)
    assert result['qualityStatus'] == 'UNSUPPORTED'
    client.get_metric_data.assert_not_called()


def test_service_quotas_embedded_error_is_operational_failure():
    client = Mock()
    q = quota()
    q['ErrorReason'] = {'ErrorCode': 'DEPENDENCY_ACCESS_DENIED_ERROR', 'ErrorMessage': 'denied'}
    result, = fetch_metrics(ctx_for(client), [q], NOW-timedelta(minutes=20), NOW)
    assert result['qualityStatus'] == 'ERROR'
    assert result['usageValue'] is None
    client.get_metric_data.assert_not_called()
