from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cloudformation as checks
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants


STACK_SET = 'parent-stack-set'
STACK_SET_ID = 'parent-stack-set:11111111-2222-3333-4444-555555555555'


def context(code='L-255FC6A0'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cloudformation', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def summary(name=STACK_SET, identity=STACK_SET_ID):
    return {'StackSetName': name, 'StackSetId': identity, 'Status': 'ACTIVE'}


def test_dependencies_per_stack_set_use_described_auto_deployment_configuration():
    second_name = 'second-stack-set'
    second_id = 'second-stack-set:11111111-2222-3333-4444-555555555555'
    ctx = context()
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_stack_sets', {'Summaries': [summary(), summary(second_name, second_id)]},
                          {'Status': 'ACTIVE'})
        stub.add_response('describe_stack_set', {'StackSet': {
            'StackSetName': STACK_SET, 'StackSetId': STACK_SET_ID, 'Status': 'ACTIVE',
            'AutoDeployment': {'Enabled': True, 'DependsOn': ['arn:dependency:1', 'arn:dependency:2']}}},
            {'StackSetName': STACK_SET})
        stub.add_response('describe_stack_set', {'StackSet': {
            'StackSetName': second_name, 'StackSetId': second_id, 'Status': 'ACTIVE'}},
            {'StackSetName': second_name})
        result = checks.dependencies_per_stack_set(ctx)
        assert (result['usage'], result['resource_id']) == (2, STACK_SET_ID)
        assert 'arn:dependency' not in str(result)
        stub.assert_no_pending_responses()


def operation(identity, status):
    return {'OperationId': identity, 'Action': 'UPDATE', 'Status': status}


def test_queued_operations_are_paginated_deduplicated_and_counted_per_stack_set():
    ctx = context('L-AC58B440')
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_stack_sets', {'Summaries': [summary()]}, {'Status': 'ACTIVE'})
        stub.add_response('list_stack_set_operations', {
            'Summaries': [operation('queued-1', 'QUEUED'), operation('running', 'RUNNING')],
            'NextToken': 'next'}, {'StackSetName': STACK_SET})
        stub.add_response('list_stack_set_operations', {
            'Summaries': [operation('queued-1', 'QUEUED'), operation('queued-2', 'QUEUED')]},
            {'StackSetName': STACK_SET, 'NextToken': 'next'})
        result = checks.queued_operations_per_stack_set(ctx)
        assert (result['usage'], result['resource_id']) == (2, STACK_SET_ID)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('detail', [
    {},
    {'StackSet': {'StackSetName': 'other', 'Status': 'ACTIVE'}},
    {'StackSet': {'StackSetName': STACK_SET, 'Status': 'DELETED'}},
    {'StackSet': {'StackSetName': STACK_SET, 'AutoDeployment': []}},
    {'StackSet': {'StackSetName': STACK_SET, 'AutoDeployment': {'DependsOn': [None]}}},
    {'StackSet': {'StackSetName': STACK_SET,
                  'AutoDeployment': {'DependsOn': ['arn:one', 'arn:one']}}},
])
def test_incomplete_or_inconsistent_stack_set_details_are_unknown(detail):
    ctx = Mock()
    ctx.call.side_effect = [[summary()], detail]
    with pytest.raises(NoData):
        checks.stack_set_details(ctx)


@pytest.mark.parametrize('operations', [
    [{'OperationId': 'operation', 'Status': 'FUTURE'}],
    [{'Status': 'QUEUED'}],
    [operation('same', 'QUEUED'), operation('same', 'RUNNING')],
])
def test_invalid_stack_set_operation_inventory_is_unknown(operations):
    ctx = Mock()
    ctx.call.side_effect = [[summary()], operations]
    with pytest.raises(NoData):
        checks.queued_operations_per_stack_set(ctx)


def test_cloudformation_catalog_code_and_new_permissions_are_exact():
    keys = custom_keys()
    assert ('cloudformation', 'L-DCC58E6D') in keys
    assert ('cloudformation', 'L-DCC58D6E') not in keys
    assert {('cloudformation', 'L-255FC6A0'), ('cloudformation', 'L-AC58B440')} <= keys
    for action in ('DescribeStackSet', 'ListStackSetOperations'):
        assert grants(f'cloudformation:{action}')
