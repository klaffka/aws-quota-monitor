"""Greengrass V1 group scopes, reached through their definition version ARNs."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import greengrass
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 17, tzinfo=UTC).isoformat()
ACCOUNT = 'arn:aws:greengrass:eu-central-1:123456789012'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'greengrass', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in greengrass.CHECKS if quota == code)


def definition_arn(kind, identity='def-1', version='ver-1'):
    return f'{ACCOUNT}:/greengrass/definition/{kind}/{identity}/versions/{version}'


def stub_group(stub, kinds):
    """Stub a group whose version names one definition ARN per given kind."""
    stub.add_response('list_groups', {'Groups': [
        {'Id': 'group-1', 'Name': 'one', 'Arn': f'{ACCOUNT}:/greengrass/groups/group-1',
         'LatestVersion': 'gv-1', 'CreationTimestamp': MOMENT,
         'LastUpdatedTimestamp': MOMENT}]}, {})
    stub.add_response('get_group_version', {
        'Id': 'group-1', 'Version': 'gv-1',
        'Definition': {key: definition_arn(kind) for kind, key in kinds.items()}},
        {'GroupId': 'group-1', 'GroupVersionId': 'gv-1'})


def test_devices_are_counted_from_the_definition_the_group_version_names():
    ctx = context('L-172983AD')
    with Stubber(ctx.client('greengrass')) as stub:
        stub_group(stub, {'devices': 'DeviceDefinitionVersionArn'})
        stub.add_response('get_device_definition_version', {
            'Id': 'def-1', 'Version': 'ver-1',
            'Definition': {'Devices': [
                {'Id': 'd1', 'ThingArn': 'arn:thing/a', 'CertificateArn': 'arn:cert/a'},
                {'Id': 'd2', 'ThingArn': 'arn:thing/b', 'CertificateArn': 'arn:cert/b'}]}},
            {'DeviceDefinitionId': 'def-1', 'DeviceDefinitionVersionId': 'ver-1'})
        result = check('L-172983AD')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'group-1')
        stub.assert_no_pending_responses()


def test_a_group_naming_no_definition_counts_as_zero():
    """A group need not hold every kind of definition."""
    ctx = context('L-172983AD')
    with Stubber(ctx.client('greengrass')) as stub:
        stub_group(stub, {})
        assert check('L-172983AD')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_an_arn_that_is_not_a_definition_version_is_reported():
    """Guessing an id out of an unexpected ARN would measure the wrong thing."""
    ctx = context('L-172983AD')
    with Stubber(ctx.client('greengrass')) as stub:
        stub.add_response('list_groups', {'Groups': [
            {'Id': 'group-1', 'Name': 'one', 'Arn': f'{ACCOUNT}:/greengrass/groups/group-1',
             'LatestVersion': 'gv-1', 'CreationTimestamp': MOMENT,
             'LastUpdatedTimestamp': MOMENT}]}, {})
        stub.add_response('get_group_version', {
            'Id': 'group-1', 'Version': 'gv-1',
            'Definition': {'DeviceDefinitionVersionArn': f'{ACCOUNT}:/greengrass/definition/devices/def-1'}},
            {'GroupId': 'group-1', 'GroupVersionId': 'gv-1'})
        with pytest.raises(NoData, match='definition version'):
            check('L-172983AD')(ctx)


def subscription(identity, source):
    return {'Id': identity, 'Source': source, 'Subject': 'topic/a', 'Target': 'cloud'}


@pytest.mark.parametrize('code, expected', [
    ('L-AC2D5DCC', 3),   # every subscription
    ('L-59276CBA', 1),   # only those the cloud sends
])
def test_cloud_sourced_subscriptions_are_told_apart(code, expected):
    ctx = context(code)
    with Stubber(ctx.client('greengrass')) as stub:
        stub_group(stub, {'subscriptions': 'SubscriptionDefinitionVersionArn'})
        stub.add_response('get_subscription_definition_version', {
            'Id': 'def-1', 'Version': 'ver-1',
            'Definition': {'Subscriptions': [
                subscription('s1', 'cloud'),
                subscription('s2', 'arn:thing/a'),
                subscription('s3', 'arn:function/b')]}},
            {'SubscriptionDefinitionId': 'def-1', 'SubscriptionDefinitionVersionId': 'ver-1'})
        assert check(code)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def function(identity, resources=0):
    return {'Id': identity, 'FunctionArn': f'arn:lambda/{identity}',
            'FunctionConfiguration': {'Environment': {'ResourceAccessPolicies': [
                {'ResourceId': f'r{index}', 'Permission': 'ro'} for index in range(resources)]}}}


@pytest.mark.parametrize('code, expected, resource', [
    ('L-F7F6CD87', 2, 'group-1'),          # functions in the group
    ('L-966A9851', 4, 'group-1/hungry'),   # resources on the busiest function
])
def test_functions_and_their_resource_policies_come_from_one_definition(code, expected, resource):
    ctx = context(code)
    with Stubber(ctx.client('greengrass')) as stub:
        stub_group(stub, {'functions': 'FunctionDefinitionVersionArn'})
        stub.add_response('get_function_definition_version', {
            'Id': 'def-1', 'Version': 'ver-1',
            'Definition': {'Functions': [function('hungry', resources=4),
                                         function('plain', resources=1)]}},
            {'FunctionDefinitionId': 'def-1', 'FunctionDefinitionVersionId': 'ver-1'})
        result = check(code)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, resource)
        stub.assert_no_pending_responses()


def test_resources_are_counted_from_the_resource_definition():
    ctx = context('L-56EE2BF6')
    with Stubber(ctx.client('greengrass')) as stub:
        stub_group(stub, {'resources': 'ResourceDefinitionVersionArn'})
        stub.add_response('get_resource_definition_version', {
            'Id': 'def-1', 'Version': 'ver-1',
            'Definition': {'Resources': [
                {'Id': 'r1', 'Name': 'one', 'ResourceDataContainer': {}}]}},
            {'ResourceDefinitionId': 'def-1', 'ResourceDefinitionVersionId': 'ver-1'})
        assert check('L-56EE2BF6')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
