"""Amazon FSx regional file-system resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def file_systems(ctx):
    return ctx.call('fsx', 'describe_file_systems', 'FileSystems')


def count_type(ctx, file_system_type, deployment_type=None):
    count = 0
    for fs in file_systems(ctx):
        if fs.get('FileSystemType') != file_system_type:
            continue
        if deployment_type and fs.get('LustreConfiguration', {}).get('DeploymentType') != deployment_type:
            continue
        count += 1
    return dict(usage=count, source='fsx:DescribeFileSystems', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-C28C1403', 'ONTAP file systems', lambda ctx: count_type(ctx, 'ONTAP')),
    ('L-5B89F9CE', 'Windows file systems', lambda ctx: count_type(ctx, 'WINDOWS')),
    ('L-59D0763F', 'OpenZFS file systems', lambda ctx: count_type(ctx, 'OPENZFS')),
    ('L-9AFA1F09', 'Lustre Persistent_1 file systems', lambda ctx: count_type(ctx, 'LUSTRE', 'PERSISTENT_1')),
    ('L-FD6F2F22', 'Lustre Persistent_2 file systems', lambda ctx: count_type(ctx, 'LUSTRE', 'PERSISTENT_2')),
    ('L-C48231E5', 'Lustre Scratch file systems', lambda ctx: count_type(ctx, 'LUSTRE', 'SCRATCH_1')),
    ('L-60836D3E', 'Lustre Cache_1 caches', lambda ctx: count_type(ctx, 'LUSTRE', 'CACHE_1')),
]


def get_current_quotastatus_fsx(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'fsx' for service, _ in context.quotas):
        return []
    return context.run('fsx', CHECKS, skip)
