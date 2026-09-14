"""Amazon EBS volume, snapshot and archive quotas.

Storage and IOPS modification quotas apply to everything modified within a
rolling six-hour window rather than to a current inventory, and the direct-API
request quotas are per-second rates, so neither is measured here. Concurrent
snapshot copies and concurrent volume copy operations are in-flight cross-Region
operations that no API lists.
"""
from collections import Counter, defaultdict
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

EC2 = 'ec2'
GIB_PER_TIB = 1024
VOLUME_TYPES = {'standard', 'io1', 'io2', 'gp2', 'gp3', 'sc1', 'st1'}
ARCHIVE_IN_PROGRESS = 'archival-in-progress'
RESTORE_IN_PROGRESS = {'temporary-restore-in-progress', 'permanent-restore-in-progress'}


def volumes(ctx):
    """Return this Region's volumes keyed by volume ID."""
    found = {}
    for volume in ctx.call(EC2, 'describe_volumes', 'Volumes'):
        identity = volume.get('VolumeId')
        if not isinstance(identity, str) or not identity:
            raise NoData('EBS volume is missing its identity')
        if volume.get('VolumeType') not in VOLUME_TYPES:
            raise NoData('EBS volume has an unknown type')
        if not isinstance(volume.get('Size'), int):
            raise NoData('EBS volume has no size')
        if identity in found and found[identity] != volume:
            raise NoData('EBS volume inventory changed during pagination')
        found[identity] = volume
    return found


def snapshots(ctx):
    """Return the snapshots this account owns, keyed by snapshot ID."""
    found = {}
    for snapshot in ctx.call(EC2, 'describe_snapshots', 'Snapshots', OwnerIds=['self']):
        identity = snapshot.get('SnapshotId')
        if not isinstance(identity, str) or not identity:
            raise NoData('EBS snapshot is missing its identity')
        if identity in found and found[identity] != snapshot:
            raise NoData('EBS snapshot inventory changed during pagination')
        found[identity] = snapshot
    return found


def tier_status(ctx):
    result = []
    for item in ctx.call(EC2, 'describe_snapshot_tier_status', 'SnapshotTierStatuses'):
        if not isinstance(item.get('SnapshotId'), str):
            raise NoData('EBS snapshot tier status is missing its snapshot')
        result.append(item)
    return result


def _storage_tib(volume_type):
    def check(ctx):
        size = sum(volume['Size'] for volume in volumes(ctx).values()
                   if volume['VolumeType'] == volume_type)
        return dict(usage=size / GIB_PER_TIB, source='ec2:DescribeVolumes',
                    method='ACCOUNT_COUNT')
    return check


def _provisioned_iops(volume_type):
    def check(ctx):
        total = 0
        for volume in volumes(ctx).values():
            if volume['VolumeType'] != volume_type:
                continue
            iops = volume.get('Iops')
            if not isinstance(iops, int):
                raise NoData('Provisioned IOPS volume has no IOPS')
            total += iops
        return dict(usage=total, source='ec2:DescribeVolumes', method='ACCOUNT_COUNT')
    return check


def _pending_per_volume(ctx):
    """Count snapshots still being created, keyed by their source volume."""
    inventory = volumes(ctx)
    counts = Counter()
    for snapshot in snapshots(ctx).values():
        if snapshot.get('State') != 'pending':
            continue
        volume = snapshot.get('VolumeId')
        if volume not in inventory:
            # The source volume is gone, so the snapshot cannot be attributed
            # to a type without undercounting one of them.
            raise NoData('Pending EBS snapshot has no source volume')
        counts[volume] += 1
    return inventory, counts


def _concurrent_snapshots(volume_type):
    def check(ctx):
        inventory, counts = _pending_per_volume(ctx)
        values = [(identity, counts[identity], None)
                  for identity, volume in inventory.items()
                  if volume['VolumeType'] == volume_type]
        return maximum(values, 'EBSVolume', 'ec2:DescribeSnapshots')
    return check


def archived_snapshots_per_volume(ctx):
    counts = defaultdict(int)
    for item in tier_status(ctx):
        if item.get('StorageTier') != 'archive':
            continue
        volume = item.get('VolumeId')
        if not isinstance(volume, str) or not volume:
            raise NoData('Archived EBS snapshot has no source volume')
        counts[volume] += 1
    return maximum(((volume, count, None) for volume, count in counts.items()),
                   'EBSVolume', 'ec2:DescribeSnapshotTierStatus')


def _tiering_operations(states):
    def check(ctx):
        usage = sum(item.get('LastTieringOperationStatus') in states
                    for item in tier_status(ctx))
        return dict(usage=usage, source='ec2:DescribeSnapshotTierStatus',
                    method='ACCOUNT_COUNT')
    return check


def fast_snapshot_restores(ctx):
    """Count the Region's enabled and transitioning fast snapshot restores."""
    usage = 0
    for item in ctx.call(EC2, 'describe_fast_snapshot_restores', 'FastSnapshotRestores'):
        state = item.get('State')
        if state is None:
            raise NoData('Fast snapshot restore has no state')
        if state in {'enabling', 'optimizing', 'enabled'}:
            usage += 1
    return dict(usage=usage, source='ec2:DescribeFastSnapshotRestores',
                method='ACCOUNT_COUNT')


STORAGE_QUOTAS = (
    ('L-9CF3C2EB', 'standard', 'Magnetic (standard)'),
    ('L-D18FCD1D', 'gp2', 'General Purpose SSD (gp2)'),
    ('L-7A658B76', 'gp3', 'General Purpose SSD (gp3)'),
    ('L-FD252861', 'io1', 'Provisioned IOPS SSD (io1)'),
    ('L-09BD8365', 'io2', 'Provisioned IOPS SSD (io2)'),
    ('L-17AF77E8', 'sc1', 'Cold HDD (sc1)'),
    ('L-82ACEF56', 'st1', 'Throughput Optimized HDD (st1)'),
)

CONCURRENT_SNAPSHOT_QUOTAS = (
    ('L-750405C3', 'standard', 'Magnetic (standard)'),
    ('L-835364B2', 'gp2', 'General Purpose SSD (gp2)'),
    ('L-D8F37C68', 'gp3', 'General Purpose SSD (gp3)'),
    ('L-DB70D580', 'io1', 'Provisioned IOPS SSD (io1)'),
    ('L-D0291BE3', 'io2', 'Provisioned IOPS SSD (io2)'),
    ('L-915A3DBB', 'sc1', 'Cold HDD (sc1)'),
    ('L-9F6E7C4E', 'st1', 'Throughput Optimized HDD (st1)'),
)

CHECKS = [
    ('L-309BACF6', 'Snapshots per Region',
     lambda ctx: dict(usage=len(snapshots(ctx)), source='ec2:DescribeSnapshots',
                      method='ACCOUNT_COUNT')),
    ('L-631ECBD3', 'Fast snapshot restore', fast_snapshot_restores),
    ('L-E20676C1', 'Archived snapshots per volume', archived_snapshots_per_volume),
    ('L-3A0E616D', 'In-progress snapshot archives per account',
     _tiering_operations({ARCHIVE_IN_PROGRESS})),
    ('L-07399329', 'In-progress snapshot restores from archive per account',
     _tiering_operations(RESTORE_IN_PROGRESS)),
    ('L-B3A130E6', 'IOPS for Provisioned IOPS SSD (io1) volumes',
     _provisioned_iops('io1')),
    ('L-8D977E7E', 'IOPS for Provisioned IOPS SSD (io2) volumes',
     _provisioned_iops('io2')),
    *[(code, f'Storage for {label} volumes, in TiB', _storage_tib(volume_type))
      for code, volume_type, label in STORAGE_QUOTAS],
    *[(code, f'Concurrent snapshots per {label} volume',
       _concurrent_snapshots(volume_type))
      for code, volume_type, label in CONCURRENT_SNAPSHOT_QUOTAS],
]


def get_current_quotastatus_ebs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ebs' for service, _ in context.quotas):
        return []
    return context.run('ebs', CHECKS, skip)
