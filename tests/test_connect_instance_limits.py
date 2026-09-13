from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.connect import (
    CHECKS, INTEGRATION_SPECS, LIST_SPECS, get_current_quotastatus_connect,
    instance_limit, parent_inventory,
)
from modules.qmcore.aws import CheckContext, NoData


ARN = 'arn:aws:connect:eu-central-1:123456789012:instance/first'
CODE = 'L-9A46857E'


def quota(code=CODE, arn=ARN, value=100):
    return {'ServiceCode': 'connect', 'QuotaCode': code, 'Value': value,
            'QuotaContext': {'ContextId': arn, 'ContextScope': 'RESOURCE',
                             'ContextScopeType': 'AWS::Connect::Instance'}}


def context(code=CODE):
    # The catalog default must never replace the actual instance's applied limit.
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [quota(code, '*', 50)], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in CHECKS if candidate == code)


def test_highest_utilization_can_have_lower_raw_usage_and_is_paginated():
    ctx = context()
    second = ARN.replace('first', 'second')
    with Stubber(ctx.client('connect')) as connect, Stubber(ctx.client('service-quotas')) as sq:
        connect.add_response('list_instances', {'InstanceSummaryList': [{'Id': 'first', 'Arn': ARN}], 'NextToken': 'next'}, {})
        connect.add_response('list_instances', {'InstanceSummaryList': [{'Id': 'second', 'Arn': second}]}, {'NextToken': 'next'})
        sq.add_response('get_service_quota', {'Quota': quota(value=100)},
                        {'ServiceCode': 'connect', 'QuotaCode': CODE, 'ContextId': ARN})
        sq.add_response('get_service_quota', {'Quota': quota(arn=second, value=1000)},
                        {'ServiceCode': 'connect', 'QuotaCode': CODE, 'ContextId': second})
        connect.add_response('list_users', {'UserSummaryList': [{'Id': str(i)} for i in range(40)], 'NextToken': 'users'}, {'InstanceId': 'first'})
        connect.add_response('list_users', {'UserSummaryList': [{'Id': str(i)} for i in range(40, 80)]}, {'InstanceId': 'first', 'NextToken': 'users'})
        connect.add_response('list_users', {'UserSummaryList': [{'Id': str(i)} for i in range(100)]}, {'InstanceId': 'second'})
        row, = get_current_quotastatus_connect(ctx=ctx)
        assert (row['qualityStatus'], row['usageValue'], row['limitValue'], row['utilizationPct']) == ('OK', 80, 100, 80)
        assert row['maxResourceId'] == ARN
        sq.assert_no_pending_responses()
        connect.assert_no_pending_responses()


@pytest.mark.parametrize('bad', [
    quota(arn='*'), quota(code='L-other'), quota(value=0), quota(value=float('nan')),
    {**quota(), 'ErrorReason': {'ErrorCode': 'DEPENDENCY_ACCESS_DENIED_ERROR'}},
    {**quota(), 'QuotaContext': {}}, {**quota(), 'ServiceCode': 'eks'},
])
def test_unresolved_resource_limits_do_not_fall_back_to_catalog(bad):
    ctx = Mock()
    ctx.call.return_value = {'Quota': bad}
    with pytest.raises(NoData):
        instance_limit(ctx, CODE, ARN)


def test_denied_later_instance_does_not_return_partial_maximum():
    ctx = context()
    second = ARN.replace('first', 'second')
    with Stubber(ctx.client('connect')) as connect, Stubber(ctx.client('service-quotas')) as sq:
        connect.add_response('list_instances', {'InstanceSummaryList': [
            {'Id': 'first', 'Arn': ARN}, {'Id': 'second', 'Arn': second}]}, {})
        sq.add_response('get_service_quota', {'Quota': quota()},
                        {'ServiceCode': 'connect', 'QuotaCode': CODE, 'ContextId': ARN})
        connect.add_response('list_users', {'UserSummaryList': []}, {'InstanceId': 'first'})
        sq.add_client_error('get_service_quota', 'AccessDeniedException', expected_params={
            'ServiceCode': 'connect', 'QuotaCode': CODE, 'ContextId': second})
        row, = get_current_quotastatus_connect(ctx=ctx)
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        assert row['utilizationPct'] is None


@pytest.mark.parametrize('code,name,method,key,filters', LIST_SPECS)
def test_instance_inventory_apis_and_filters_match_sdk(code, name, method, key, filters):
    ctx = context(code)
    with Stubber(ctx.client('connect')) as connect, Stubber(ctx.client('service-quotas')) as sq:
        connect.add_response('list_instances', {'InstanceSummaryList': [{'Id': 'first', 'Arn': ARN}]}, {})
        sq.add_response('get_service_quota', {'Quota': quota(code)},
                        {'ServiceCode': 'connect', 'QuotaCode': code, 'ContextId': ARN})
        response = {key: []}
        if method == 'search_email_addresses':
            response['ApproximateTotalCount'] = 99
        connect.add_response(method, response, {'InstanceId': 'first', **filters})
        assert check(code)(ctx)['usage'] == 0
        connect.assert_no_pending_responses()


@pytest.mark.parametrize('code,kind', INTEGRATION_SPECS)
def test_integration_types_are_filtered_independently(code, kind):
    ctx = context(code)
    with Stubber(ctx.client('connect')) as connect, Stubber(ctx.client('service-quotas')) as sq:
        connect.add_response('list_instances', {'InstanceSummaryList': [{'Id': 'first', 'Arn': ARN}]}, {})
        sq.add_response('get_service_quota', {'Quota': quota(code)},
                        {'ServiceCode': 'connect', 'QuotaCode': code, 'ContextId': ARN})
        connect.add_response('list_integration_associations', {'IntegrationAssociationSummaryList': [
            {'IntegrationAssociationId': 'association', 'IntegrationType': kind}]},
                             {'InstanceId': 'first', 'IntegrationType': kind})
        assert check(code)(ctx)['usage'] == 1
        connect.assert_no_pending_responses()


def test_routing_profile_channels_and_manual_lists_have_independent_limits():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'routing'}],
        [{'QueueId': 'same', 'Channel': channel} for channel in ['VOICE', 'CHAT', 'TASK']],
        [{'QueueId': str(i), 'Channel': 'VOICE'} for i in range(4)],
    ]
    usage, child, source = parent_inventory(ctx, 'instance', 'list_routing_profiles',
        'RoutingProfileSummaryList', 'list_routing_profile_queues',
        'RoutingProfileQueueConfigSummaryList', 'RoutingProfileId', manual=True)
    assert usage == 4  # Neither one distinct queue nor 3+4 combinations.
    assert child == 'routing/manual-assignment'
    assert 'list_routing_profile_manual_assignment_queues' in source


def test_primary_attributes_count_flags_per_table_without_summing_tables():
    ctx = Mock()
    ctx.call.side_effect = [[{'Id': 'one'}, {'Id': 'two'}],
                            [{'Primary': True}, {'Primary': False}],
                            [{'Primary': True}, {'Primary': True}]]
    result = parent_inventory(ctx, 'instance', 'list_data_tables', 'DataTableSummaryList',
                              'list_data_table_attributes', 'Attributes', 'DataTableId', primary=True)
    assert result[:2] == (2, 'two')


def test_missing_primary_flag_is_unknown():
    ctx = Mock()
    ctx.call.side_effect = [[{'Id': 'one'}], [{}]]
    with pytest.raises(NoData):
        parent_inventory(ctx, 'instance', 'list_data_tables', 'DataTableSummaryList',
                         'list_data_table_attributes', 'Attributes', 'DataTableId', primary=True)


def test_missing_instance_identity_is_unknown():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'first'}]
    with pytest.raises(NoData):
        check(CODE)(ctx)


def test_empty_instance_inventory_is_zero_without_resource_limit_calls():
    ctx = context()
    with Stubber(ctx.client('connect')) as connect:
        connect.add_response('list_instances', {'InstanceSummaryList': []}, {})
        row, = get_current_quotastatus_connect(ctx=ctx)
        assert row['qualityStatus'] == 'OK'
        assert row['usageValue'] == 0
        assert row['maxResourceId'] is None
