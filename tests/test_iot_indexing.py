"""IoT fleet-index custom fields and fleet-metric percentile values."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iot
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 15, tzinfo=timezone.utc)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'iot', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in iot.CHECKS if quota == code)


CONFIGURATION = {
    'thingIndexingConfiguration': {
        'thingIndexingMode': 'REGISTRY',
        'customFields': [{'name': 'one', 'type': 'String'},
                         {'name': 'two', 'type': 'Number'}]},
    'thingGroupIndexingConfiguration': {
        'thingGroupIndexingMode': 'ON',
        'customFields': [{'name': 'three', 'type': 'String'}]}}


@pytest.mark.parametrize('code, expected', [('L-AE68DCD9', 2), ('L-8B2A08E6', 1)])
def test_each_index_counts_only_its_own_custom_fields(code, expected):
    ctx = context(code)
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('get_indexing_configuration', CONFIGURATION, {})
        assert check(code)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def test_an_index_without_custom_fields_reports_zero_not_missing_data():
    """Indexing may be off; that is a measured zero, not an absent measurement."""
    ctx = context('L-AE68DCD9')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('get_indexing_configuration',
                          {'thingIndexingConfiguration': {'thingIndexingMode': 'OFF'}}, {})
        assert check('L-AE68DCD9')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_missing_index_section_is_reported_as_no_data():
    ctx = context('L-8B2A08E6')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('get_indexing_configuration',
                          {'thingIndexingConfiguration': {'thingIndexingMode': 'OFF'}}, {})
        with pytest.raises(NoData, match='thingGroupIndexingConfiguration'):
            check('L-8B2A08E6')(ctx)


def test_percentile_values_use_the_largest_fleet_metric():
    """A non-percentile aggregation carries no values and counts as zero."""
    ctx = context('L-24513B55')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_fleet_metrics', {'fleetMetrics': [
            {'metricName': 'counted', 'metricArn': 'arn:one'},
            {'metricName': 'percentiles', 'metricArn': 'arn:two'}]}, {})
        stub.add_response('describe_fleet_metric', {
            'metricName': 'counted', 'aggregationType': {'name': 'Statistics'},
            'creationDate': MOMENT, 'lastModifiedDate': MOMENT}, {'metricName': 'counted'})
        stub.add_response('describe_fleet_metric', {
            'metricName': 'percentiles',
            'aggregationType': {'name': 'Percentiles', 'values': ['50', '90', '99']},
            'creationDate': MOMENT, 'lastModifiedDate': MOMENT}, {'metricName': 'percentiles'})
        result = check('L-24513B55')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'percentiles')
        stub.assert_no_pending_responses()


def test_a_fleet_metric_whose_detail_names_another_metric_is_refused():
    ctx = context('L-24513B55')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_fleet_metrics',
                          {'fleetMetrics': [{'metricName': 'asked', 'metricArn': 'arn:one'}]}, {})
        stub.add_response('describe_fleet_metric',
                          {'metricName': 'answered', 'creationDate': MOMENT,
                           'lastModifiedDate': MOMENT}, {'metricName': 'asked'})
        with pytest.raises(NoData, match='different identity'):
            check('L-24513B55')(ctx)
