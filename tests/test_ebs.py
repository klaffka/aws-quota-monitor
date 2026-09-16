import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ebs
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

GP3 = 'vol-00000000000000001'
IO2 = 'vol-00000000000000002'
SNAPSHOT = 'snap-00000000000000001'


def context(code='L-309BACF6'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ebs', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def volume(identity=GP3, kind='gp3', size=512, iops=None):
    result = {'VolumeId': identity, 'VolumeType': kind, 'Size': size, 'State': 'in-use'}
    if iops is not None:
        result['Iops'] = iops
    return result


def snapshot(identity=SNAPSHOT, volume_id=GP3, state='completed'):
    return {'SnapshotId': identity, 'VolumeId': volume_id, 'State': state}


def tier(snapshot_id=SNAPSHOT, volume_id=GP3, storage_tier='archive', status=None):
    result = {'SnapshotId': snapshot_id, 'VolumeId': volume_id, 'StorageTier': storage_tier}
    if status is not None:
        result['LastTieringOperationStatus'] = status
    return result


def check(code):
    return next(fn for quota, _, fn in ebs.CHECKS if quota == code)


def test_storage_is_reported_per_volume_type_in_tebibytes():
    ctx = context('L-7A658B76')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [
            volume(size=1024), volume(IO2, 'io2', 2048, iops=3000)]}, {})
        # Only the gp3 volume counts towards the gp3 quota.
        assert check('L-7A658B76')(ctx)['usage'] == 1.0
        stub.assert_no_pending_responses()


def test_provisioned_iops_are_summed_for_their_own_volume_type():
    ctx = context('L-8D977E7E')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [
            volume(IO2, 'io2', 100, iops=5000),
            volume('vol-00000000000000003', 'io2', 100, iops=1500),
            volume(GP3, 'gp3', 100, iops=3000)]}, {})
        assert check('L-8D977E7E')(ctx)['usage'] == 6500
        stub.assert_no_pending_responses()


def test_a_provisioned_iops_volume_without_iops_raises_nodata():
    ctx = context('L-B3A130E6')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [volume(IO2, 'io1', 100)]}, {})
        with pytest.raises(NoData, match='no IOPS'):
            check('L-B3A130E6')(ctx)


def test_an_unknown_volume_type_raises_instead_of_being_ignored():
    ctx = context('L-7A658B76')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [
            {'VolumeId': GP3, 'VolumeType': 'gp4', 'Size': 1}]}, {})
        with pytest.raises(NoData, match='unknown type'):
            check('L-7A658B76')(ctx)


def test_concurrent_snapshots_count_pending_ones_per_volume_of_that_type():
    ctx = context('L-D8F37C68')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [
            volume(GP3), volume(IO2, 'io2', 100, iops=100)]}, {})
        stub.add_response('describe_snapshots', {'Snapshots': [
            snapshot('snap-00000000000000001', GP3, 'pending'),
            snapshot('snap-00000000000000002', GP3, 'pending'),
            snapshot('snap-00000000000000003', GP3, 'completed'),
            snapshot('snap-00000000000000004', IO2, 'pending')]}, {'OwnerIds': ['self']})
        result = check('L-D8F37C68')(ctx)
        assert (result['usage'], result['resource_id']) == (2, GP3)
        stub.assert_no_pending_responses()


def test_a_pending_snapshot_of_a_deleted_volume_raises_nodata():
    ctx = context('L-D8F37C68')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': [volume(GP3)]}, {})
        stub.add_response('describe_snapshots', {'Snapshots': [
            snapshot('snap-00000000000000009', 'vol-0000000000000dead', 'pending')]},
            {'OwnerIds': ['self']})
        with pytest.raises(NoData, match='no source volume'):
            check('L-D8F37C68')(ctx)


def test_snapshots_per_region_counts_owned_snapshots_only():
    ctx = context('L-309BACF6')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_snapshots', {'Snapshots': [
            snapshot('snap-00000000000000001'), snapshot('snap-00000000000000002')]},
            {'OwnerIds': ['self']})
        assert check('L-309BACF6')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_archived_snapshots_are_counted_per_source_volume():
    ctx = context('L-E20676C1')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_snapshot_tier_status', {'SnapshotTierStatuses': [
            tier('snap-00000000000000001', GP3),
            tier('snap-00000000000000002', GP3),
            tier('snap-00000000000000003', IO2),
            tier('snap-00000000000000004', GP3, storage_tier='standard')]}, {})
        result = ebs.archived_snapshots_per_volume(ctx)
        assert (result['usage'], result['resource_id']) == (2, GP3)
        stub.assert_no_pending_responses()


def test_tiering_operations_separate_archives_from_restores():
    for code, status, expected in (('L-3A0E616D', 'archival-in-progress', 1),
                                   ('L-07399329', 'temporary-restore-in-progress', 1),
                                   ('L-07399329', 'archival-in-progress', 0)):
        ctx = context(code)
        with Stubber(ctx.client('ec2')) as stub:
            stub.add_response('describe_snapshot_tier_status', {'SnapshotTierStatuses': [
                tier(status=status)]}, {})
            assert check(code)(ctx)['usage'] == expected, (code, status)
            stub.assert_no_pending_responses()


def test_fast_snapshot_restores_count_transitioning_and_enabled_states():
    ctx = context('L-631ECBD3')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_fast_snapshot_restores', {'FastSnapshotRestores': [
            {'SnapshotId': SNAPSHOT, 'AvailabilityZone': 'eu-central-1a', 'State': 'enabled'},
            {'SnapshotId': SNAPSHOT, 'AvailabilityZone': 'eu-central-1b', 'State': 'optimizing'},
            {'SnapshotId': SNAPSHOT, 'AvailabilityZone': 'eu-central-1c', 'State': 'disabled'}]}, {})
        assert ebs.fast_snapshot_restores(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_empty_region_reports_zero():
    ctx = context('L-7A658B76')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_volumes', {'Volumes': []}, {})
        assert check('L-7A658B76')(ctx)['usage'] == 0.0
        stub.assert_no_pending_responses()


def test_every_ebs_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'ebs'}
    assert {code for code, _, _ in ebs.CHECKS} <= registered
