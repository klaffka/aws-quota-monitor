from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.lambda_checks import lambda_checks
from modules.qmcore.aws import CheckContext, Unsupported
from modules.qmcore.registry import custom_keys

PROVIDER = 'arn:aws:lambda:eu-central-1:123456789012:capacity-provider:graviton'
OTHER_PROVIDER = 'arn:aws:lambda:eu-central-1:123456789012:capacity-provider:x86'
IMAGE = 'arn:aws:lambda:eu-central-1:123456789012:microvm-image/base'
NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'lambda', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in lambda_checks.CHECKS if quota == code)


def test_function_versions_are_counted_per_capacity_provider():
    ctx = context('L-96779E29')
    with Stubber(ctx.client('lambda')) as stub:
        provider = {'State': 'Active',
                    'VpcConfig': {'SubnetIds': ['subnet-1'],
                                  'SecurityGroupIds': ['sg-1']},
                    'PermissionsConfig': {'CapacityProviderOperatorRoleArn':
                                          'arn:aws:iam::123456789012:role/lambda'}}
        stub.add_response('list_capacity_providers', {'CapacityProviders': [
            dict(provider, CapacityProviderArn=PROVIDER),
            dict(provider, CapacityProviderArn=OTHER_PROVIDER)]}, {})
        stub.add_response('list_function_versions_by_capacity_provider',
                          {'CapacityProviderArn': PROVIDER, 'FunctionVersions': [
                              {'FunctionArn': 'a', 'State': 'Active'},
                              {'FunctionArn': 'b', 'State': 'Active'}]},
                          {'CapacityProviderName': PROVIDER})
        stub.add_response('list_function_versions_by_capacity_provider',
                          {'CapacityProviderArn': OTHER_PROVIDER, 'FunctionVersions': [
                              {'FunctionArn': 'c', 'State': 'Active'}]},
                          {'CapacityProviderName': OTHER_PROVIDER})
        result = lambda_checks.versions_per_capacity_provider(ctx)
        assert (result['usage'], result['resource_id']) == (2, PROVIDER)
        stub.assert_no_pending_responses()


def test_a_capacity_provider_without_an_arn_is_reported_as_unsupported():
    with pytest.raises(Unsupported, match='missing its identity'):
        lambda_checks._identity({}, 'CapacityProviderArn', 'capacity provider')


def test_microvm_image_versions_are_counted_per_image():
    ctx = context('L-F8BECE9C')
    with Stubber(ctx.client('lambda-microvms')) as stub:
        stub.add_response('list_microvm_images', {'items': [
            {'imageArn': IMAGE, 'name': 'base', 'state': 'ACTIVE',
             'createdAt': NOW}]}, {})
        version = {'baseImageArn': IMAGE, 'buildRoleArn':
                   'arn:aws:iam::123456789012:role/build',
                   'codeArtifact': {'uri': 's3://code/app.zip'},
                   'imageArn': IMAGE, 'state': 'ACTIVE', 'status': 'AVAILABLE',
                   'createdAt': NOW}
        stub.add_response('list_microvm_image_versions', {'items': [
            dict(version, imageVersion='1'), dict(version, imageVersion='2')]},
            {'imageIdentifier': IMAGE})
        result = lambda_checks.versions_per_microvm_image(ctx)
        assert (result['usage'], result['resource_id']) == (2, IMAGE)
        stub.assert_no_pending_responses()


def test_lambda_network_interfaces_are_counted_per_vpc():
    ctx = context('L-9FEE3D26')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_network_interfaces', {'NetworkInterfaces': [
            {'NetworkInterfaceId': 'eni-1', 'VpcId': 'vpc-1',
             'InterfaceType': 'lambda'},
            {'NetworkInterfaceId': 'eni-2', 'VpcId': 'vpc-1',
             'InterfaceType': 'lambda'},
            {'NetworkInterfaceId': 'eni-3', 'VpcId': 'vpc-2',
             'InterfaceType': 'lambda'}]},
            {'Filters': [{'Name': 'interface-type', 'Values': ['lambda']}]})
        result = lambda_checks.network_interfaces_per_vpc(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'vpc-1')
        stub.assert_no_pending_responses()


def test_every_new_lambda_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'lambda'}
    assert {code for code, _, _ in lambda_checks.CHECKS} <= registered
