import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import greengrass, quicksight
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
ARN = f'arn:aws:greengrass:eu-central-1:{ACCOUNT}:components:sensor'
OTHER_ARN = f'arn:aws:greengrass:eu-central-1:{ACCOUNT}:components:gateway'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_only_private_components_are_listed_and_counted():
    ctx = context('greengrass', 'L-4676BC3D')
    with Stubber(ctx.client('greengrassv2')) as stub:
        stub.add_response('list_components', {'components': [
            {'arn': ARN, 'componentName': 'sensor'},
            {'arn': OTHER_ARN, 'componentName': 'gateway'}]}, {'scope': 'PRIVATE'})
        assert check(greengrass, 'L-4676BC3D')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_component_versions_are_reported_per_component():
    ctx = context('greengrass', 'L-FC3754BD')
    with Stubber(ctx.client('greengrassv2')) as stub:
        stub.add_response('list_components', {'components': [
            {'arn': ARN, 'componentName': 'sensor'},
            {'arn': OTHER_ARN, 'componentName': 'gateway'}]}, {'scope': 'PRIVATE'})
        stub.add_response('list_component_versions', {'componentVersions': [
            {'componentName': 'sensor', 'componentVersion': '1.0.0', 'arn': ARN}]},
            {'arn': ARN})
        stub.add_response('list_component_versions', {'componentVersions': [
            {'componentName': 'gateway', 'componentVersion': '1.0.0', 'arn': OTHER_ARN},
            {'componentName': 'gateway', 'componentVersion': '2.0.0', 'arn': OTHER_ARN}]},
            {'arn': OTHER_ARN})
        result = greengrass.versions_per_component(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'gateway')
        stub.assert_no_pending_responses()


def test_core_device_name_length_reports_the_longest_name():
    ctx = context('greengrass', 'L-AB912DF1')
    with Stubber(ctx.client('greengrassv2')) as stub:
        stub.add_response('list_core_devices', {'coreDevices': [
            {'coreDeviceThingName': 'edge-1', 'status': 'HEALTHY'},
            {'coreDeviceThingName': 'edge-in-the-back-room', 'status': 'UNHEALTHY'}]}, {})
        result = greengrass.core_device_name_length(ctx)
        assert (result['usage'], result['resource_id']) == (
            len('edge-in-the-back-room'), 'edge-in-the-back-room')
        stub.assert_no_pending_responses()


def test_a_component_without_an_arn_raises_nodata():
    ctx = context('greengrass', 'L-4676BC3D')
    with Stubber(ctx.client('greengrassv2')) as stub:
        stub.add_response('list_components', {'components': [
            {'componentName': 'sensor'}]}, {'scope': 'PRIVATE'})
        with pytest.raises(NoData, match='missing its ARN'):
            check(greengrass, 'L-4676BC3D')(ctx)


def group(name):
    return f'arn:aws:quicksight:eu-central-1:{ACCOUNT}:group/default/{name}'


def policy(identity, assets, applicable=None, approvers=None):
    return {'PolicyId': identity,
            'PolicyArn': f'arn:aws:quicksight:eu-central-1:{ACCOUNT}:policy/{identity}',
            'Name': identity, 'Actions': ['SHARE'], 'AssetTypes': list(assets),
            'ApplicableTo': {'Type': 'GROUPS',
                             'GroupArns': list(applicable or [group('default')])},
            'ApprovalGroups': list(approvers or [group('approvers')]),
            'CreatedAt': '2026-09-15T00:00:00Z', 'UpdatedAt': '2026-09-15T00:00:00Z'}


def test_approval_policies_are_counted_per_account_and_asset_type():
    policies = [policy('p1', ['AGENT', 'SPACE']), policy('p2', ['AGENT']),
                policy('p3', ['KNOWLEDGE_BASE'])]
    for code, expected_usage, expected_id in (('L-D75C2D48', 3, None),
                                              ('L-8D8B7044', 2, 'AGENT')):
        ctx = context('quicksight', code)
        with Stubber(ctx.client('quicksight')) as stub:
            stub.add_response('list_approval_policies', {'Policies': policies}, {})
            result = check(quicksight, code)(ctx)
            assert result['usage'] == expected_usage, code
            assert result.get('resource_id') == expected_id, code
            stub.assert_no_pending_responses()


def test_applicable_and_approver_groups_are_counted_separately():
    policies = [policy('p1', ['AGENT'], applicable=[group('a')],
                       approvers=[group('x'), group('y'), group('z')]),
                policy('p2', ['SPACE'], applicable=[group('a'), group('b')],
                       approvers=[group('x')])]
    for code, expected_usage, expected_id in (('L-04458D9F', 2, 'p2'),
                                              ('L-61EC97DA', 3, 'p1')):
        ctx = context('quicksight', code)
        with Stubber(ctx.client('quicksight')) as stub:
            stub.add_response('list_approval_policies', {'Policies': policies}, {})
            result = check(quicksight, code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def test_an_unknown_asset_type_raises_nodata():
    ctx = context('quicksight', 'L-8D8B7044')
    with Stubber(ctx.client('quicksight')) as stub:
        stub.add_response('list_approval_policies', {'Policies': [
            policy('p1', ['DASHBOARD'])]}, {})
        with pytest.raises(NoData, match='unknown asset type'):
            check(quicksight, 'L-8D8B7044')(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((greengrass, 'greengrass'), (quicksight, 'quicksight')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
