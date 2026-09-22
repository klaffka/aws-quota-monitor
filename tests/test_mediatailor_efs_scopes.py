"""MediaTailor channel/source inventories and EFS mount-target scopes."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import efs, mediatailor
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 15, tzinfo=UTC)


def context(service, code, client):
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                       account='123456789012')
    return ctx, Stubber(ctx.client(client))


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def test_playback_configurations_are_an_account_total():
    ctx, stub = context('mediatailor', 'L-F60EC97B', 'mediatailor')
    with stub:
        stub.add_response('list_playback_configurations',
                          {'Items': [{'Name': 'one'}, {'Name': 'two'}]}, {})
        assert check(mediatailor, 'L-F60EC97B')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_channel_outputs_use_the_largest_channel_without_a_second_call():
    """ListChannels already carries Outputs, so no channel is described twice."""
    ctx, stub = context('mediatailor', 'L-3BCD6A29', 'mediatailor')
    with stub:
        stub.add_response('list_channels', {'Items': [
            {'ChannelName': 'small', 'Arn': 'arn:one', 'ChannelState': 'RUNNING',
             'PlaybackMode': 'LINEAR', 'Tier': 'BASIC',
             'LogConfiguration': {'LogTypes': []},
             'Outputs': [{'ManifestName': 'a', 'PlaybackUrl': 'u', 'SourceGroup': 'g'}]},
            {'ChannelName': 'large', 'Arn': 'arn:two', 'ChannelState': 'RUNNING',
             'PlaybackMode': 'LINEAR', 'Tier': 'BASIC',
             'LogConfiguration': {'LogTypes': []},
             'Outputs': [{'ManifestName': 'a', 'PlaybackUrl': 'u', 'SourceGroup': 'g'},
                         {'ManifestName': 'b', 'PlaybackUrl': 'v', 'SourceGroup': 'g'}]}]}, {})
        result = check(mediatailor, 'L-3BCD6A29')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'large')
        stub.assert_no_pending_responses()


def test_segment_delivery_configurations_use_the_largest_source_location():
    ctx, stub = context('mediatailor', 'L-680CE323', 'mediatailor')
    with stub:
        stub.add_response('list_source_locations',
                          {'Items': [{'SourceLocationName': 'loc', 'Arn': 'arn:loc',
                                      'HttpConfiguration': {'BaseUrl': 'https://example.com'}}]}, {})
        stub.add_response('describe_source_location', {
            'SourceLocationName': 'loc', 'Arn': 'arn:loc',
            'HttpConfiguration': {'BaseUrl': 'https://example.com'},
            'SegmentDeliveryConfigurations': [{'Name': 'a'}, {'Name': 'b'}, {'Name': 'c'}]},
            {'SourceLocationName': 'loc'})
        result = check(mediatailor, 'L-680CE323')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'loc')
        stub.assert_no_pending_responses()


def test_a_source_location_detail_for_another_location_is_refused():
    ctx, stub = context('mediatailor', 'L-680CE323', 'mediatailor')
    with stub:
        stub.add_response('list_source_locations',
                          {'Items': [{'SourceLocationName': 'asked', 'Arn': 'arn:loc',
                                      'HttpConfiguration': {'BaseUrl': 'https://example.com'}}]}, {})
        stub.add_response('describe_source_location',
                          {'SourceLocationName': 'answered', 'Arn': 'arn:loc',
                           'HttpConfiguration': {'BaseUrl': 'https://example.com'}},
                          {'SourceLocationName': 'asked'})
        with pytest.raises(NoData, match='different identity'):
            check(mediatailor, 'L-680CE323')(ctx)


FILE_SYSTEMS = {'FileSystems': [
    {'FileSystemId': 'fs-1', 'CreationToken': 'one', 'CreationTime': MOMENT,
     'LifeCycleState': 'available', 'NumberOfMountTargets': 3, 'OwnerId': '123456789012',
     'PerformanceMode': 'generalPurpose', 'SizeInBytes': {'Value': 0}, 'Tags': []}]}
MOUNT_TARGETS = {'MountTargets': [
    {'MountTargetId': 'fsmt-01234567890', 'FileSystemId': 'fs-1', 'SubnetId': 'subnet-0123456789abc',
     'LifeCycleState': 'available', 'VpcId': 'vpc-1'},
    {'MountTargetId': 'fsmt-01234567891', 'FileSystemId': 'fs-1', 'SubnetId': 'subnet-0123456789abd',
     'LifeCycleState': 'available', 'VpcId': 'vpc-1'},
    {'MountTargetId': 'fsmt-01234567892', 'FileSystemId': 'fs-1', 'SubnetId': 'subnet-0123456789abe',
     'LifeCycleState': 'available', 'VpcId': 'vpc-2'}]}


def test_vpcs_per_file_system_count_distinct_vpcs_not_mount_targets():
    """Three mount targets can share two VPCs; the quota counts the VPCs."""
    ctx, stub = context('elasticfilesystem', 'L-03A6A61D', 'efs')
    with stub:
        stub.add_response('describe_file_systems', FILE_SYSTEMS, {})
        stub.add_response('describe_mount_targets', MOUNT_TARGETS, {'FileSystemId': 'fs-1'})
        result = check(efs, 'L-03A6A61D')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'fs-1')
        stub.assert_no_pending_responses()


def test_security_groups_use_the_busiest_mount_target():
    ctx, stub = context('elasticfilesystem', 'L-3D348029', 'efs')
    with stub:
        stub.add_response('describe_file_systems', FILE_SYSTEMS, {})
        stub.add_response('describe_mount_targets', MOUNT_TARGETS, {'FileSystemId': 'fs-1'})
        for target, groups in [('fsmt-01234567890', ['sg-01234567']), ('fsmt-01234567891', ['sg-01234567', 'sg-01234568']),
                               ('fsmt-01234567892', [])]:
            stub.add_response('describe_mount_target_security_groups',
                              {'SecurityGroups': groups}, {'MountTargetId': target})
        result = check(efs, 'L-3D348029')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'fsmt-01234567891')
        stub.assert_no_pending_responses()
