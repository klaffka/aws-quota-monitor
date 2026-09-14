"""Amazon Neptune regional resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('neptune', method, key)), source=f'neptune:{method}', method='ACCOUNT_COUNT')


def endpoints_per_cluster(ctx):
    values = []
    for cluster in ctx.call('neptune', 'describe_db_clusters', 'DBClusters'):
        identifier = cluster.get('DBClusterIdentifier')
        if identifier:
            endpoints = ctx.call('neptune', 'describe_db_cluster_endpoints', 'DBClusterEndpoints',
                                 DBClusterIdentifier=identifier)
            values.append((identifier, len(endpoints), None))
    return maximum(values, 'DBCluster', 'neptune:DescribeDBClusterEndpoints')


def read_replicas_per_cluster(ctx):
    values = []
    instances = ctx.call('neptune', 'describe_db_instances', 'DBInstances')
    clusters = sorted({item.get('DBClusterIdentifier') for item in instances if item.get('DBClusterIdentifier')})
    for cluster in clusters:
        readers = sum(item.get('DBInstanceRole') == 'READ_REPLICA'
                      for item in instances if item.get('DBClusterIdentifier') == cluster)
        values.append((cluster, readers, None))
    return maximum(values, 'DBCluster', 'neptune:DescribeDBInstances')


CHECKS = [
    ('L-6D17A5A2', 'DB clusters', lambda ctx: count(ctx, 'describe_db_clusters', 'DBClusters')),
    ('L-368A3E00', 'DB instances', lambda ctx: count(ctx, 'describe_db_instances', 'DBInstances')),
    ('L-483F7912', 'DB subnet groups', lambda ctx: count(ctx, 'describe_db_subnet_groups', 'DBSubnetGroups')),
    ('L-D6543DBD', 'Manual DB cluster snapshots', lambda ctx: count(ctx, 'describe_db_cluster_snapshots', 'DBClusterSnapshots')),
    ('L-A425F59F', 'Cluster endpoints per DB cluster', endpoints_per_cluster),
    ('L-584DADE7', 'DB instance parameter groups', lambda ctx: count(ctx, 'describe_db_parameter_groups', 'DBParameterGroups')),
    ('L-5BB9A916', 'DB cluster parameter groups', lambda ctx: count(ctx, 'describe_db_cluster_parameter_groups', 'DBClusterParameterGroups')),
    ('L-A6A065D7', 'Read replicas per cluster', read_replicas_per_cluster),
]


def get_current_quotastatus_neptune(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'neptune' for service, _ in context.quotas): return []
    return context.run('neptune', CHECKS, skip)
