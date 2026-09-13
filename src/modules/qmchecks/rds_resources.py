"""Amazon RDS/Aurora regional inventory checks."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('rds', method, key)), source=f'rds:{method}', method='ACCOUNT_COUNT')


def custom_endpoints_per_cluster(ctx):
    values = []
    for cluster in ctx.call('rds', 'describe_db_clusters', 'DBClusters'):
        identifier = cluster.get('DBClusterIdentifier')
        if identifier:
            endpoints = ctx.call('rds', 'describe_db_cluster_endpoints', 'DBClusterEndpoints',
                                 DBClusterIdentifier=identifier)
            values.append((identifier, len(endpoints), None))
    return maximum(values, 'DBCluster', 'rds:DescribeDBClusterEndpoints')


def read_replicas_per_primary(ctx):
    grouped = {}
    for instance in ctx.call('rds', 'describe_db_instances', 'DBInstances'):
        primary = instance.get('ReadReplicaSourceDBInstanceIdentifier')
        if primary:
            grouped[primary] = grouped.get(primary, 0) + 1
    return maximum([(primary, count, None) for primary, count in grouped.items()],
                   'DBInstance', 'rds:DescribeDBInstances')


def subnets_per_subnet_group(ctx):
    values = []
    for group in ctx.call('rds', 'describe_db_subnet_groups', 'DBSubnetGroups'):
        name = group.get('DBSubnetGroupName')
        if name:
            values.append((name, len(group.get('Subnets', [])), None))
    return maximum(values, 'DBSubnetGroup', 'rds:DescribeDBSubnetGroups')


def authorizations_per_security_group(ctx):
    values = []
    for group in ctx.call('rds', 'describe_db_security_groups', 'DBSecurityGroups'):
        name = group.get('DBSecurityGroupName')
        if name:
            count = len(group.get('EC2SecurityGroups', [])) + len(group.get('IPRanges', []))
            values.append((name, count, None))
    return maximum(values, 'DBSecurityGroup', 'rds:DescribeDBSecurityGroups')


def total_storage(ctx):
    return dict(usage=sum(instance.get('AllocatedStorage', 0) or 0
                          for instance in ctx.call('rds', 'describe_db_instances', 'DBInstances')),
                source='rds:DescribeDBInstances', method='ACCOUNT_COUNT', unit='GB')


def custom_engine_versions(ctx):
    """Count custom engine versions exposed by the RDS inventory API."""
    versions = ctx.call('rds', 'describe_db_engine_versions', 'DBEngineVersions', IncludeAll=True)
    return dict(usage=sum((version.get('Engine') or '').lower().startswith('custom-')
                          for version in versions),
                source='rds:DescribeDBEngineVersions', method='ACCOUNT_COUNT')


def iam_roles_per_parent(ctx, method, key, identifier, resource_type):
    values = []
    for resource in ctx.call('rds', method, key):
        name = resource.get(identifier)
        if name:
            values.append((name, len(resource.get('AssociatedRoles', [])), None))
    return maximum(values, resource_type, f'rds:{method}')


CHECKS = [
    ('L-7B6409FD', 'DB instances', lambda ctx: resource_count(ctx, 'describe_db_instances', 'DBInstances')),
    ('L-952B80B8', 'DB clusters', lambda ctx: resource_count(ctx, 'describe_db_clusters', 'DBClusters')),
    ('L-48C6BF61', 'DB subnet groups', lambda ctx: resource_count(ctx, 'describe_db_subnet_groups', 'DBSubnetGroups')),
    ('L-D94C7EA3', 'Proxies', lambda ctx: resource_count(ctx, 'describe_db_proxies', 'DBProxies')),
    ('L-E4C808A8', 'DB cluster parameter groups',
     lambda ctx: resource_count(ctx, 'describe_db_cluster_parameter_groups', 'DBClusterParameterGroups')),
    ('L-DE55804A', 'Parameter groups', lambda ctx: resource_count(ctx, 'describe_db_parameter_groups', 'DBParameterGroups')),
    ('L-9FA33840', 'Option groups', lambda ctx: resource_count(ctx, 'describe_option_groups', 'OptionGroups')),
    ('L-272F1212', 'Manual DB instance snapshots', lambda ctx: resource_count(ctx, 'describe_db_snapshots', 'DBSnapshots')),
    ('L-9B510759', 'Manual DB cluster snapshots', lambda ctx: resource_count(ctx, 'describe_db_cluster_snapshots', 'DBClusterSnapshots')),
    ('L-75AC651F', 'DB shard groups', lambda ctx: resource_count(ctx, 'describe_db_shard_groups', 'DBShardGroups')),
    ('L-9372BAB3', 'Custom endpoints per DB cluster', custom_endpoints_per_cluster),
    ('L-A59F4C87', 'Event subscriptions', lambda ctx: resource_count(ctx, 'describe_event_subscriptions', 'EventSubscriptions')),
    ('L-5BC124EF', 'Read replicas per primary', read_replicas_per_primary),
    ('L-6F3ACC36', 'Subnets per DB subnet group', subnets_per_subnet_group),
    ('L-AA8B1026', 'Authorizations per DB security group', authorizations_per_security_group),
    ('L-CB9BE6F8', 'Integrations', lambda ctx: resource_count(ctx, 'describe_integrations', 'Integrations')),
    ('L-7ADDB58A', 'Total storage for all DB instances', total_storage),
    ('L-732153D0', 'Security groups', lambda ctx: resource_count(ctx, 'describe_db_security_groups', 'DBSecurityGroups')),
    ('L-78E853F4', 'Reserved DB instances', lambda ctx: resource_count(ctx, 'describe_reserved_db_instances', 'ReservedDBInstances')),
    ('L-A399AC0B', 'Custom engine versions', custom_engine_versions),
    ('L-DD2301CA', 'IAM roles per DB instance',
     lambda ctx: iam_roles_per_parent(ctx, 'describe_db_instances', 'DBInstances',
                                      'DBInstanceIdentifier', 'DBInstance')),
    ('L-E094F43D', 'IAM roles per DB cluster',
     lambda ctx: iam_roles_per_parent(ctx, 'describe_db_clusters', 'DBClusters',
                                      'DBClusterIdentifier', 'DBCluster')),
]


def get_current_quotastatus_rds_resources(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rds' for service, _ in context.quotas):
        return []
    return context.run('rds', CHECKS, skip)
