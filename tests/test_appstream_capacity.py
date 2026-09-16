import json
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.appstream import CHECKS, get_current_quotastatus_appstream
from modules.qmchecks.appstream_capacity import (
    CHECKS as CAPACITY_CHECKS, fleet_instances, image_sharing, instance_usage, platform_usage,
)
from modules.qmchecks.appstream_quotas import INSTANCE_QUOTAS, PLATFORM_QUOTAS
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys


def context(quotas=()):
    return CheckContext(boto3.Session(region_name='eu-central-1'), quotas, account='123456789012')


def fleet(name='fleet', instance_type='stream.standard.large', **fields):
    result = dict(Name=name, Arn=f'arn:aws:appstream:eu-central-1:123456789012:fleet/{name}',
                  InstanceType=instance_type, FleetType='ON_DEMAND', State='RUNNING',
                  ImageName='native', ComputeCapacityStatus={'Desired': 5, 'Available': 4, 'InUse': 1})
    result.update(fields)
    return result


def test_fleet_capacity_includes_idle_instances_and_separates_byol_with_pagination():
    ctx = context()
    with Stubber(ctx.client('appstream')) as stub:
        stub.add_response('describe_fleets', {'Fleets': [fleet()], 'NextToken': 'next'}, {})
        stub.add_response('describe_fleets', {'Fleets': [
            fleet('byol', ImageName='byol'), fleet('second'), fleet('stopped', State='STOPPED'),
            fleet('elastic', FleetType='ELASTIC'), fleet('different', 'stream.compute.large')]},
                          {'NextToken': 'next'})
        for name, kind in [('native', 'NATIVE'), ('byol', 'BYOL')]:
            stub.add_response('describe_images', {'Images': [{'Name': name, 'ImageType': kind}]},
                              {'Names': [name]})
        assert instance_usage(ctx, 'stream.standard.large', 'NATIVE', 'fleet')['usage'] == 10
        assert instance_usage(ctx, 'stream.standard.large', 'BYOL', 'fleet')['usage'] == 5
        # Both checks reuse the entire fleet inventory and each image lookup.
        stub.assert_no_pending_responses()


def test_imported_type_matches_exactly_without_requiring_native_image_metadata():
    ctx = context()
    with Stubber(ctx.client('appstream')) as stub:
        stub.add_response('describe_fleets', {'Fleets': [fleet(instance_type='GeneralPurpose.m6a.2xlarge')]}, {})
        assert instance_usage(ctx, 'GeneralPurpose.m6a.2xlarge', 'CUSTOM', 'fleet')['usage'] == 5
        assert instance_usage(ctx, 'GeneralPurpose.m6a.xlarge', 'CUSTOM', 'fleet')['usage'] == 0


@pytest.mark.parametrize('capacity,fields', [
    ({'Desired': 9, 'Available': 4, 'InUse': 1}, {}),
    ({'Desired': 2, 'Available': 4, 'InUse': 1}, {}),
    ({'Desired': 5, 'Running': 5}, {}),
    ({'Desired': 5, 'Available': -1, 'InUse': 6}, {}),
    ({'Desired': True, 'Available': 0, 'InUse': 1}, {}),
    ({'Desired': 5, 'Available': 4, 'InUse': 1}, {'State': 'STARTING'}),
    ({'Desired': 5, 'Available': 4, 'InUse': 1}, {'State': 'STOPPING'}),
    ({'Desired': 5, 'Running': 5, 'Draining': 1}, {'MaxSessionsPerInstance': 3}),
    ({'Desired': 5, 'ActualUserSessions': 20}, {'MaxSessionsPerInstance': 4}),
])
def test_ambiguous_capacity_never_becomes_a_precise_count(capacity, fields):
    with pytest.raises(NoData):
        fleet_instances(fleet(ComputeCapacityStatus=capacity, **fields))


def test_multi_session_counts_instances_not_user_slots():
    item = fleet(MaxSessionsPerInstance=4, ComputeCapacityStatus={
        'Desired': 5, 'Running': 5, 'DesiredUserSessions': 20, 'ActualUserSessions': 20})
    assert fleet_instances(item) == 5
    assert fleet_instances(fleet(State='STOPPED')) == 0


def test_image_builder_image_type_and_unresolved_stopped_accounting():
    ctx = context()
    with Stubber(ctx.client('appstream')) as stub:
        arn = 'arn:aws:appstream:eu-central-1:123456789012:image/byol'
        stub.add_response('describe_image_builders', {'ImageBuilders': [
            {'Name': 'one', 'InstanceType': 'stream.standard.large', 'State': 'RUNNING', 'ImageArn': arn},
            {'Name': 'two', 'InstanceType': 'stream.standard.large', 'State': 'RUNNING', 'ImageArn': arn}]}, {})
        stub.add_response('describe_images', {'Images': [{'Name': 'byol', 'ImageType': 'BYOL'}]}, {'Arns': [arn]})
        assert instance_usage(ctx, 'stream.standard.large', 'BYOL', 'image_builder')['usage'] == 2
        assert instance_usage(ctx, 'stream.standard.large', 'NATIVE', 'image_builder')['usage'] == 0
    ctx = Mock()
    ctx.call.return_value = [{'InstanceType': 'GeneralPurpose.m6a.large', 'State': 'STOPPED'}]
    with pytest.raises(NoData, match='outside RUNNING'):
        instance_usage(ctx, 'GeneralPurpose.m6a.large', 'CUSTOM', 'image_builder')


@pytest.mark.parametrize('images', [[], [{'Name': 'native'}], [{'Name': 'native', 'ImageType': 'UNKNOWN'}]])
def test_missing_image_scope_is_not_assumed_to_be_native(images):
    ctx = Mock()
    ctx.call.side_effect = [[fleet()], images]
    with pytest.raises(NoData):
        instance_usage(ctx, 'stream.standard.large', 'NATIVE', 'fleet')


def test_later_inventory_page_error_is_preserved_by_collector():
    code = next(code for code, typ, kind, inv in INSTANCE_QUOTAS
                if typ == 'stream.standard.large' and kind == 'NATIVE' and inv == 'fleet')
    ctx = context([{'ServiceCode': 'appstream2', 'QuotaCode': code, 'Value': 10}])
    with Stubber(ctx.client('appstream')) as stub:
        stub.add_response('describe_fleets', {'Fleets': [fleet()], 'NextToken': 'next'}, {})
        stub.add_client_error('describe_fleets', service_error_code='AccessDeniedException',
                              expected_params={'NextToken': 'next'})
        skip = {('appstream2', code) for code, _, _ in CHECKS}
        row, = get_current_quotastatus_appstream(ctx=ctx, skip=skip)
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        assert get_current_quotastatus_appstream(ctx=ctx, skip=skip | {('appstream2', code)}) == []


def test_elastic_sessions_include_disconnected_and_all_authentication_methods():
    ctx = context()
    with Stubber(ctx.client('appstream')) as stub:
        stub.add_response('describe_fleets', {'Fleets': [
            fleet(FleetType='ELASTIC', Platform='WINDOWS_SERVER_2019'),
            fleet('linux', FleetType='ELASTIC', Platform='UBUNTU_PRO_2404')]}, {})
        stub.add_response('list_associated_stacks', {'Names': ['stack']}, {'FleetName': 'fleet'})
        session = dict(Id='shared-id', UserId='user', StackName='stack', FleetName='fleet',
                       State='ACTIVE', ConnectionState='NOT_CONNECTED')
        for auth in ('API', 'SAML', 'USERPOOL', 'AWS_AD'):
            item = dict(session, Id='other-id') if auth == 'SAML' else session
            stub.add_response('describe_sessions', {'Sessions': [item]},
                              {'StackName': 'stack', 'FleetName': 'fleet', 'AuthenticationType': auth})
        assert platform_usage(ctx, 'stream.standard.large', 'WINDOWS_SERVER_2019', 'elastic_session')['usage'] == 2
        stub.assert_no_pending_responses()


def test_platform_builder_count_includes_stopped_resource_and_filters_platform():
    ctx = Mock()
    ctx.call.return_value = [
        {'InstanceType': 'stream.standard.large', 'Platform': 'WINDOWS_SERVER_2019', 'State': 'STOPPED'},
        {'InstanceType': 'stream.standard.large', 'Platform': 'OTHER'},
        {'InstanceType': 'stream.standard.small', 'Platform': 'WINDOWS_SERVER_2019'}]
    assert platform_usage(ctx, 'stream.standard.large', 'WINDOWS_SERVER_2019', 'app_block_builder')['usage'] == 1


def test_sharing_permissions_use_sdk_shape_and_maximum_per_image():
    ctx = context()
    with Stubber(ctx.client('appstream')) as stub:
        stub.add_response('describe_images', {'Images': [{'Name': 'one'}, {'Name': 'two'}]}, {'Type': 'PRIVATE'})
        permission = {'sharedAccountId': '999999999999', 'imagePermissions': {'allowFleet': True}}
        stub.add_response('describe_image_permissions', {'SharedImagePermissionsList': [permission], 'NextToken': 'next'}, {'Name': 'one'})
        stub.add_response('describe_image_permissions', {'SharedImagePermissionsList': [permission]}, {'Name': 'one', 'NextToken': 'next'})
        stub.add_response('describe_image_permissions', {'SharedImagePermissionsList': []}, {'Name': 'two'})
        assert image_sharing(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_every_instance_and_platform_mapping_matches_catalog_scope():
    catalog = {q['QuotaCode']: q for q in json.loads(Path('tests/fixtures/selected-service-quotas.json').read_text())
               if q['ServiceCode'] == 'appstream2'}
    expected = {code for code, q in catalog.items() if q['QuotaName'].endswith((' for fleets', ' for image builders'))}
    assert {row[0] for row in INSTANCE_QUOTAS} == expected
    assert len(INSTANCE_QUOTAS) == len(expected) == 502
    for code, typ, kind, inventory in INSTANCE_QUOTAS:
        q = catalog[code]
        assert typ in q['QuotaName'] or typ in q['Description']
        assert (kind == 'BYOL') == q['QuotaName'].startswith('BYOL ')
        assert (kind == 'CUSTOM') == (not typ.startswith('stream.'))
        assert q['QuotaName'].endswith(' for fleets' if inventory == 'fleet' else ' for image builders')
    keys = {('appstream2', code) for code, _, _ in CAPACITY_CHECKS}
    assert len(keys) == len(CAPACITY_CHECKS) == 525
    assert keys <= custom_keys()


# How the catalog spells each platform the mapping uses. A new platform has to
# be added here, which is the point: the enum value is not the display name.
PLATFORM_NAMES = {'AMAZON_LINUX2': 'Amazon Linux 2',
                  'UBUNTU_PRO_2404': 'Ubuntu Pro 2404',
                  'WINDOWS_SERVER_2019': 'Windows Server 2019'}
INVENTORY_PREFIXES = {'elastic_session': 'Max concurrent sessions for Elastic fleets with ',
                      'app_block_builder': 'Max app block builders with '}


def test_every_platform_mapping_matches_its_catalog_name():
    """A platform row is only as good as the name it claims to describe, and a
    wrong instance type or platform measures a different fleet entirely."""
    from scripts.quota_coverage import load_catalog

    catalog = {quota['QuotaCode']: quota.get('QuotaName') or ''
               for quota in load_catalog('tests/fixtures/quota-catalog-union.json')
               if quota['ServiceCode'] == 'appstream2'}
    for code, instance_type, platform, inventory in PLATFORM_QUOTAS:
        name = catalog[code]
        assert name.startswith(INVENTORY_PREFIXES[inventory]), code
        assert name.endswith(f'{instance_type} instance type'), code
        assert f'{PLATFORM_NAMES[platform]} platform' in name, code
