"""Amazon EFS file system and access point inventories.

Service Quotas calls the service `elasticfilesystem`, which is also its IAM
prefix, but the SDK client is named `efs`.

`Mount targets per Availability Zone` and `Mount targets per VPC` stay in the
audit. Neither names whose mount targets it counts, and no export states a
value that would settle it: the same listing supports an account total and a
per-file-system maximum, and picking one would be a denominator chosen by
guess.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

EFS = 'efs'
SERVICE = 'elasticfilesystem'


def file_systems(ctx):
    found = []
    for file_system in ctx.call(EFS, 'describe_file_systems', 'FileSystems'):
        identity = file_system.get('FileSystemId')
        if not isinstance(identity, str) or not identity:
            raise NoData('EFS file system is missing its identity')
        found.append(identity)
    return found


def access_points_per_file_system(ctx):
    values = []
    for identity in file_systems(ctx):
        points = ctx.call(EFS, 'describe_access_points', 'AccessPoints',
                          FileSystemId=identity)
        values.append((identity, len(points), None))
    return maximum(values, 'FileSystem', 'elasticfilesystem:DescribeAccessPoints')


def mount_targets(ctx):
    """Yield (file system, mount target) pairs; the listing needs a parent."""
    for identity in file_systems(ctx):
        for target in ctx.call(EFS, 'describe_mount_targets', 'MountTargets',
                               FileSystemId=identity):
            yield identity, target


def vpcs_per_file_system(ctx):
    """A file system reaches a VPC through its mount targets."""
    vpcs = {}
    for identity in file_systems(ctx):
        found = set()
        for target in ctx.call(EFS, 'describe_mount_targets', 'MountTargets',
                               FileSystemId=identity):
            vpc = target.get('VpcId')
            if vpc:
                found.add(vpc)
        vpcs[identity] = len(found)
    return maximum([(identity, count, None) for identity, count in vpcs.items()],
                   'FileSystem', 'elasticfilesystem:DescribeMountTargets')


def security_groups_per_mount_target(ctx):
    values = []
    for _identity, target in mount_targets(ctx):
        mount_target = target.get('MountTargetId')
        if not isinstance(mount_target, str) or not mount_target:
            raise NoData('EFS mount target is missing its identity')
        groups = ctx.call(EFS, 'describe_mount_target_security_groups',
                          MountTargetId=mount_target).get('SecurityGroups')
        if not isinstance(groups, list):
            raise NoData('EFS mount target has no security group list')
        values.append((mount_target, len(groups), None))
    return maximum(values, 'FileSystemMountTarget',
                   'elasticfilesystem:DescribeMountTargetSecurityGroups')


CHECKS = [
    ('L-03A6A61D', 'VPCs per file system', vpcs_per_file_system),
    ('L-3D348029', 'Security groups per mount target', security_groups_per_mount_target),
    ('L-848C634D', 'File systems per account',
     lambda ctx: dict(usage=len(file_systems(ctx)),
                      source='elasticfilesystem:DescribeFileSystems',
                      method='ACCOUNT_COUNT')),
    ('L-4CCB99B3', 'Access points per file system', access_points_per_file_system),
]


def get_current_quotastatus_efs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    return context.run(SERVICE, CHECKS, skip)
