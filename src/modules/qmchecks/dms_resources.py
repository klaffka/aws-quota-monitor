"""AWS DMS regional resource inventories."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('dms', method, key)), source=f'dms:{method}', method='ACCOUNT_COUNT')


def data_migrations(ctx):
    return ctx.call('dms', 'describe_data_migrations', 'DataMigrations')


def running_data_migrations(ctx):
    """A migration that has started and not ended is still running.

    DataMigrationStatus is a plain string in the service model, with no
    documented set of values, so the timestamps decide rather than a guessed
    status vocabulary that a new AWS state would silently fall out of.
    """
    usage = sum(bool(migration.get('DataMigrationStartTime'))
                and not migration.get('DataMigrationEndTime')
                for migration in data_migrations(ctx))
    return dict(usage=usage, source='dms:DescribeDataMigrations(started, not ended)',
                method='ACCOUNT_COUNT')


def migrations_per_project(ctx):
    totals = {}
    for migration in data_migrations(ctx):
        project = migration.get('MigrationProjectArn')
        if not project:
            raise NoData('DMS data migration names no migration project')
        totals[project] = totals.get(project, 0) + 1
    return maximum([(project, count, None) for project, count in totals.items()],
                   'DMSMigrationProject', 'dms:DescribeDataMigrations')


def subnets_per_subnet_group(ctx):
    return maximum([(group.get('ReplicationSubnetGroupIdentifier'),
                     len(group.get('Subnets') or ()), None)
                    for group in ctx.call('dms', 'describe_replication_subnet_groups',
                                          'ReplicationSubnetGroups')],
                   'DMSSubnetGroup', 'dms:DescribeReplicationSubnetGroups')


CHECKS = [
    ('L-4182EDE9', 'Subnets per subnet group', subnets_per_subnet_group),
    ('L-D97343A2', 'Event subscriptions',
     lambda ctx: count(ctx, 'describe_event_subscriptions', 'EventSubscriptionsList')),
    ('L-E569F59D', 'Serverless replications',
     lambda ctx: count(ctx, 'describe_replications', 'Replications')),
    ('L-8D962DAE', 'Number of DMS Fleet Advisor collector instances',
     lambda ctx: count(ctx, 'describe_fleet_advisor_collectors', 'Collectors')),
    ('L-62EFB27A', 'Number of Data Migrations per Migration Project', migrations_per_project),
    ('L-FBEA20FB', 'Number of running Data Migrations', running_data_migrations),
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
