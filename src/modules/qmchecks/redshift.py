from modules.qmcore.aws import CheckContext, maximum, session_from_env
def total_nodes(ctx):
    return dict(usage=sum(x.get('NumberOfNodes',0) for x in ctx.call('redshift','describe_clusters','Clusters')),source='redshift:DescribeClusters',method='ACCOUNT_COUNT')
def nodes_per_cluster(ctx):
    return maximum([(x.get('ClusterIdentifier'),x.get('NumberOfNodes',0),None) for x in ctx.call('redshift','describe_clusters','Clusters')],'Cluster','redshift:DescribeClusters')


def nodes_per_cluster_type(ctx, node_type):
    return maximum([(x.get('ClusterIdentifier'), x.get('NumberOfNodes', 0), None)
                    for x in ctx.call('redshift', 'describe_clusters', 'Clusters')
                    if str(x.get('NodeType', '')).lower().startswith(node_type.lower())],
                   'Cluster', 'redshift:DescribeClusters')
def count(ctx, method, key):
    return dict(usage=len(ctx.call('redshift', method, key)),
                source=f'redshift:{method}', method='ACCOUNT_COUNT')


CHECKS=[('L-F9D462EE','Nodes',total_nodes),
        ('L-BB966966', 'Nodes in a cluster', nodes_per_cluster),
        ('L-93AC8AE6', 'RA3 nodes in a cluster', lambda ctx: nodes_per_cluster_type(ctx, 'ra3')),
        ('L-84537943', 'DC2 nodes in a cluster', lambda ctx: nodes_per_cluster_type(ctx, 'dc2')),
        ('L-890444C0', 'Security groups', lambda ctx: count(ctx, 'describe_cluster_security_groups', 'ClusterSecurityGroups')),
        ('L-7C6A532D', 'Cluster IAM roles', lambda ctx: maximum(
            [(x.get('ClusterIdentifier'), len(x.get('IamRoles', [])), None)
             for x in ctx.call('redshift', 'describe_clusters', 'Clusters')],
            'Cluster', 'redshift:DescribeClusters')),
        ('L-2E428669', 'Snapshots', lambda ctx: count(ctx, 'describe_cluster_snapshots', 'Snapshots')),
        ('L-A3830BB3', 'Parameter groups', lambda ctx: count(ctx, 'describe_cluster_parameter_groups', 'ClusterParameterGroups')),
        ('L-BE12F428', 'Subnet groups', lambda ctx: count(ctx, 'describe_cluster_subnet_groups', 'ClusterSubnetGroups'))]
def get_current_quotastatus_redshift(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('redshift',CHECKS,skip) if any(s=='redshift' for s,_ in c.quotas) else []
