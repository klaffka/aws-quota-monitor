"""Amazon DynamoDB Accelerator cluster, node and group quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DAX = 'dax'


def clusters(ctx):
    found = {}
    for cluster in ctx.call(DAX, 'describe_clusters', 'Clusters'):
        name = cluster.get('ClusterName')
        if not isinstance(name, str) or not name:
            raise NoData('DAX cluster is missing its name')
        total = cluster.get('TotalNodes')
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise NoData('DAX cluster has no node count')
        found[name] = cluster
    return found


def nodes_per_cluster(ctx):
    values = [(name, cluster['TotalNodes'], None)
              for name, cluster in clusters(ctx).items()]
    return maximum(values, 'DAXCluster', 'dax:DescribeClusters')


def total_nodes(ctx):
    usage = sum(cluster['TotalNodes'] for cluster in clusters(ctx).values())
    return dict(usage=usage, source='dax:DescribeClusters', method='ACCOUNT_COUNT')


def subnets_per_subnet_group(ctx):
    values = []
    for group in ctx.call(DAX, 'describe_subnet_groups', 'SubnetGroups'):
        name = group.get('SubnetGroupName')
        if not isinstance(name, str) or not name:
            raise NoData('DAX subnet group is missing its name')
        subnets = group.get('Subnets') or []
        if not isinstance(subnets, list):
            raise NoData('DAX subnet group has an invalid subnet list')
        values.append((name, len(subnets), None))
    return maximum(values, 'DAXSubnetGroup', 'dax:DescribeSubnetGroups')


CHECKS = [
    ('L-AB139030', 'Total number of nodes', total_nodes),
    ('L-87AEEBB5', 'Nodes per cluster', nodes_per_cluster),
    ('L-315AFD08', 'Parameter groups',
     lambda ctx: dict(usage=len(ctx.call(DAX, 'describe_parameter_groups',
                                         'ParameterGroups')),
                      source='dax:DescribeParameterGroups', method='ACCOUNT_COUNT')),
    ('L-F55BD408', 'Subnet groups',
     lambda ctx: dict(usage=len(ctx.call(DAX, 'describe_subnet_groups', 'SubnetGroups')),
                      source='dax:DescribeSubnetGroups', method='ACCOUNT_COUNT')),
    ('L-E34C284B', 'Subnets per subnet group', subnets_per_subnet_group),
]


def get_current_quotastatus_dax(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dax' for service, _ in context.quotas):
        return []
    return context.run('dax', CHECKS, skip)
