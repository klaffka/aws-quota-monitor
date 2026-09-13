"""AWS DMS regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('dms', method, key)), source=f'dms:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-E17328E9', 'Endpoint count', lambda ctx: count(ctx, 'describe_endpoints', 'Endpoints')),
    ('L-C2341CDC', 'Replication instances', lambda ctx: count(ctx, 'describe_replication_instances', 'ReplicationInstances')),
    ('L-7FD3593B', 'Task count', lambda ctx: count(ctx, 'describe_replication_tasks', 'ReplicationTasks')),
    ('L-FE918D88', 'Certificate count', lambda ctx: count(ctx, 'describe_certificates', 'Certificates')),
    ('L-27B24FAD', 'Subnet groups', lambda ctx: count(ctx, 'describe_replication_subnet_groups', 'ReplicationSubnetGroups')),
    ('L-DE63148C', 'Migration projects', lambda ctx: count(ctx, 'describe_migration_projects', 'MigrationProjects')),
    ('L-9A47CA81', 'Data providers', lambda ctx: count(ctx, 'describe_data_providers', 'DataProviders')),
    ('L-1AB41EE0', 'Data migrations', lambda ctx: count(ctx, 'describe_data_migrations', 'DataMigrations')),
    ('L-D12045C2', 'Instance profiles', lambda ctx: count(ctx, 'describe_instance_profiles', 'InstanceProfiles')),
]


def get_current_quotastatus_dms_resources(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dms' for service, _ in context.quotas): return []
    return context.run('dms', CHECKS, skip)
