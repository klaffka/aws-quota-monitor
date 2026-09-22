"""IoT FleetWise signal catalog, campaign and state template scopes."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iotfleetwise
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 17, tzinfo=UTC)
ARN = 'arn:aws:iotfleetwise:eu-central-1:123456789012'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'iotfleetwise', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in iotfleetwise.CHECKS if quota == code)


def test_signal_catalog_nodes_come_from_the_counts_the_detail_reports():
    """GetSignalCatalog reports the totals, so the nodes are never listed."""
    ctx = context('L-FE285ED4')
    with Stubber(ctx.client('iotfleetwise')) as stub:
        stub.add_response('list_signal_catalogs', {'summaries': [
            {'name': 'big', 'arn': f'{ARN}:signal-catalog/big'},
            {'name': 'small', 'arn': f'{ARN}:signal-catalog/small'}]}, {})
        stub.add_response('get_signal_catalog', {
            'name': 'big', 'arn': f'{ARN}:signal-catalog/big',
            'creationTime': MOMENT, 'lastModificationTime': MOMENT,
            'nodeCounts': {'totalNodes': 120, 'totalSensors': 100}}, {'name': 'big'})
        stub.add_response('get_signal_catalog', {
            'name': 'small', 'arn': f'{ARN}:signal-catalog/small',
            'creationTime': MOMENT, 'lastModificationTime': MOMENT,
            'nodeCounts': {'totalNodes': 4}}, {'name': 'small'})
        result = check('L-FE285ED4')(ctx)
        assert (result['usage'], result['resource_id']) == (120, 'big')
        stub.assert_no_pending_responses()


def test_a_signal_catalog_without_a_node_count_is_reported():
    ctx = context('L-FE285ED4')
    with Stubber(ctx.client('iotfleetwise')) as stub:
        stub.add_response('list_signal_catalogs',
                          {'summaries': [{'name': 'bare', 'arn': f'{ARN}:signal-catalog/bare'}]}, {})
        stub.add_response('get_signal_catalog',
                          {'name': 'bare', 'arn': f'{ARN}:signal-catalog/bare',
                           'creationTime': MOMENT, 'lastModificationTime': MOMENT},
                          {'name': 'bare'})
        with pytest.raises(NoData, match='node count'):
            check('L-FE285ED4')(ctx)


def campaign_detail(name, signals=0, partitions=0):
    detail = {'name': name, 'arn': f'{ARN}:campaign/{name}',
              'signalCatalogArn': f'{ARN}:signal-catalog/one',
              'targetArn': f'{ARN}:fleet/one', 'status': 'RUNNING',
              'signalsToCollect': [{'name': f'sig{index}'} for index in range(signals)]}
    if partitions:
        detail['dataPartitions'] = [
            {'id': f'p{index}',
             'storageOptions': {'maximumSize': {'unit': 'MB', 'value': 1},
                                'storageLocation': '/tmp',
                                'minimumTimeToLive': {'unit': 'HOURS', 'value': 1}}}
            for index in range(partitions)]
    return detail


@pytest.mark.parametrize('code, expected, resource', [
    ('L-86E70888', 3, 'wide'),      # signals in a campaign
    ('L-A0A396E0', 2, 'split'),     # partitions in a campaign
])
def test_campaign_scopes_take_the_largest_campaign(code, expected, resource):
    ctx = context(code)
    with Stubber(ctx.client('iotfleetwise')) as stub:
        stub.add_response('list_campaigns', {'campaignSummaries': [
            {'name': 'wide', 'arn': f'{ARN}:campaign/wide',
             'creationTime': MOMENT, 'lastModificationTime': MOMENT},
            {'name': 'split', 'arn': f'{ARN}:campaign/split',
             'creationTime': MOMENT, 'lastModificationTime': MOMENT}]}, {})
        stub.add_response('get_campaign', campaign_detail('wide', signals=3), {'name': 'wide'})
        stub.add_response('get_campaign', campaign_detail('split', signals=1, partitions=2),
                          {'name': 'split'})
        result = check(code)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, resource)
        stub.assert_no_pending_responses()


def state_template(name, properties=0, data=0, metadata=0):
    return {'name': name, 'arn': f'{ARN}:state-template/{name}',
            'signalCatalogArn': f'{ARN}:signal-catalog/one',
            'stateTemplateProperties': [f'prop{index}' for index in range(properties)],
            'dataExtraDimensions': [f'data{index}' for index in range(data)],
            'metadataExtraDimensions': [f'meta{index}' for index in range(metadata)]}


@pytest.mark.parametrize('code, expected', [
    ('L-300E5FB4', 5),   # signals for a state template
    ('L-6BE0F5F7', 2),   # data dimensions
    ('L-0FDD56E9', 3),   # metadata dimensions
])
def test_the_three_state_template_scopes_read_the_same_detail(code, expected):
    ctx = context(code)
    with Stubber(ctx.client('iotfleetwise')) as stub:
        stub.add_response('list_state_templates', {'summaries': [
            {'name': 'full', 'arn': f'{ARN}:state-template/full'}]}, {})
        stub.add_response('get_state_template',
                          state_template('full', properties=5, data=2, metadata=3),
                          {'identifier': 'full'})
        assert check(code)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()
