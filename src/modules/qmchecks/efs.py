"""Amazon EFS file system and access point inventories.

Service Quotas calls the service `elasticfilesystem`, which is also its IAM
prefix, but the SDK client is named `efs`.
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


CHECKS = [
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
