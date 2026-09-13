"""MemoryDB regional resource quotas backed by Describe APIs."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def clusters(ctx):
    return ctx.call('memorydb', 'describe_clusters', 'Clusters')


def count(ctx, method, key):
    return ctx.call('memorydb', method, key)


def nodes_per_cluster(ctx):
    return maximum([(c.get('Name'), sum(s.get('NumberOfNodes', len(s.get('Nodes', [])))
                                        for s in c.get('Shards', [])), None)
                    for c in clusters(ctx)], 'Cluster', 'memorydb:DescribeClusters')


CHECKS = [
    ('L-7BC2A09E', 'Nodes per Region (MemoryDB)',
     lambda c: dict(usage=sum(sum(s.get('NumberOfNodes', len(s.get('Nodes', [])))
                                 for s in cluster.get('Shards', [])) for cluster in clusters(c)),
                    source='memorydb:DescribeClusters', method='ACCOUNT_COUNT')),
    ('L-A1C3C09E', 'Nodes per cluster (Cluster mode enabled) (MemoryDB)', nodes_per_cluster),
    ('L-4BFB02AA', 'User Groups per Region (MemoryDB)',
     lambda c: dict(usage=len(count(c, 'describe_acls', 'ACLs')), source='memorydb:DescribeACLs', method='ACCOUNT_COUNT')),
    ('L-9DDCFD10', 'Users per User Group (MemoryDB)',
     lambda c: maximum([(a.get('Name'), len(a.get('UserNames', [])), None)
                        for a in count(c, 'describe_acls', 'ACLs')], 'UserGroup', 'memorydb:DescribeACLs')),
    ('L-95D39780', 'Users per Region (MemoryDB)',
     lambda c: dict(usage=len(count(c, 'describe_users', 'Users')), source='memorydb:DescribeUsers', method='ACCOUNT_COUNT')),
    ('L-8B9CD3D0', 'Subnet groups per Region (MemoryDB)',
     lambda c: dict(usage=len(count(c, 'describe_subnet_groups', 'SubnetGroups')), source='memorydb:DescribeSubnetGroups', method='ACCOUNT_COUNT')),
    ('L-63EE95F8', 'Subnets per subnet group (MemoryDB)',
     lambda c: maximum([(s.get('Name'), len(s.get('Subnets', [])), None)
                        for s in count(c, 'describe_subnet_groups', 'SubnetGroups')], 'SubnetGroup', 'memorydb:DescribeSubnetGroups')),
    ('L-48695EA8', 'Parameter groups per Region (MemoryDB)',
     lambda c: dict(usage=len(count(c, 'describe_parameter_groups', 'ParameterGroups')), source='memorydb:DescribeParameterGroups', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_memorydb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'memorydb' for service, _ in context.quotas):
        return []
    return context.run('memorydb', CHECKS, skip)
