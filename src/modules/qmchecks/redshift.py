"""Amazon Redshift cluster, snapshot and subnet group quotas."""
from collections import defaultdict

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env
def total_nodes(ctx):
    return dict(usage=sum(x.get('NumberOfNodes',0) for x in ctx.call('redshift','describe_clusters','Clusters')),source='redshift:DescribeClusters',method='ACCOUNT_COUNT')
def nodes_per_cluster(ctx):
    return maximum([(x.get('ClusterIdentifier'),x.get('NumberOfNodes',0),None) for x in ctx.call('redshift','describe_clusters','Clusters')],'Cluster','redshift:DescribeClusters')


def nodes_per_cluster_type(ctx, node_type):
    return maximum([(x.get('ClusterIdentifier'), x.get('NumberOfNodes', 0), None)
                    for x in ctx.call('redshift', 'describe_clusters', 'Clusters')
                    if str(x.get('NodeType', '')).lower().startswith(node_type.lower())],
                   'Cluster', 'redshift:DescribeClusters')
def snapshots(ctx):
    """Return every snapshot with the accounts it has been shared with."""
    found = []
    for snapshot in ctx.call('redshift', 'describe_cluster_snapshots', 'Snapshots'):
        identity = snapshot.get('SnapshotIdentifier')
        if not isinstance(identity, str) or not identity:
            raise NoData('Redshift snapshot is missing its identity')
        accounts = snapshot.get('AccountsWithRestoreAccess') or []
        if not isinstance(accounts, list):
            raise NoData('Redshift snapshot has an invalid restore access list')
        found.append((identity, snapshot.get('KmsKeyId'), accounts))
    return found


def restore_accounts_per_snapshot(ctx):
    return maximum(((identity, len(accounts), None)
                    for identity, _, accounts in snapshots(ctx)),
                   'ClusterSnapshot', 'redshift:DescribeClusterSnapshots')


def restore_accounts_per_key(ctx):
    """One account authorised on several snapshots of a key counts once."""
    per_key = defaultdict(set)
    for _, key, accounts in snapshots(ctx):
        if key is None:
            continue
        for account in accounts:
            identity = account.get('AccountId')
            if not isinstance(identity, str) or not identity:
                raise NoData('Redshift snapshot names an account without an ID')
            per_key[key].add(identity)
    return maximum(((key, len(accounts), None) for key, accounts in per_key.items()),
                   'KmsKey', 'redshift:DescribeClusterSnapshots')


def subnets_per_group(ctx):
    values = []
    for group in ctx.call('redshift', 'describe_cluster_subnet_groups',
                          'ClusterSubnetGroups'):
        subnets = group.get('Subnets')
        if not isinstance(subnets, list):
            raise NoData('Redshift subnet group has no subnet list')
        values.append((group.get('ClusterSubnetGroupName'), len(subnets), None))
    return maximum(values, 'ClusterSubnetGroup',
                   'redshift:DescribeClusterSubnetGroups')


def count(ctx, method, key):
    return dict(usage=len(ctx.call('redshift', method, key)),
                source=f'redshift:{method}', method='ACCOUNT_COUNT')


CHECKS=[('L-F9D462EE','Nodes',total_nodes),
        ('L-BB966966', 'Nodes in a cluster', nodes_per_cluster),
        ('L-93AC8AE6', 'RA3 nodes in a cluster', lambda ctx: nodes_per_cluster_type(ctx, 'ra3')),
        ('L-84537943', 'DC2 nodes in a cluster', lambda ctx: nodes_per_cluster_type(ctx, 'dc2')),
        ('L-890444C0', 'Security groups', lambda ctx: count(ctx, 'describe_cluster_security_groups', 'ClusterSecurityGroups')),
        ('L-7C6A532D',
         'Cluster IAM roles for Amazon Redshift to access other AWS services',
         lambda ctx: maximum(
            [(x.get('ClusterIdentifier'), len(x.get('IamRoles', [])), None)
             for x in ctx.call('redshift', 'describe_clusters', 'Clusters')],
            'Cluster', 'redshift:DescribeClusters')),
        ('L-2E428669', 'Snapshots', lambda ctx: count(ctx, 'describe_cluster_snapshots', 'Snapshots')),
        ('L-A3830BB3', 'Parameter groups', lambda ctx: count(ctx, 'describe_cluster_parameter_groups', 'ClusterParameterGroups')),
        ('L-BE12F428', 'Subnet groups', lambda ctx: count(ctx, 'describe_cluster_subnet_groups', 'ClusterSubnetGroups')),
        ('L-2B30DCFE', 'Event subscriptions',
         lambda ctx: count(ctx, 'describe_event_subscriptions', 'EventSubscriptionsList')),
        ('L-58C8C0E8', 'Reserved nodes',
         lambda ctx: count(ctx, 'describe_reserved_nodes', 'ReservedNodes')),
        ('L-6C6B6042', 'Subnets in a subnet group', subnets_per_group),
        ('L-909949E5',
         'AWS accounts that you can authorize to restore a snapshot per snapshot',
         restore_accounts_per_snapshot),
        ('L-7097B286',
         'AWS accounts that you can authorize to restore a snapshot per AWS KMS key',
         restore_accounts_per_key)]
def get_current_quotastatus_redshift(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('redshift',CHECKS,skip) if any(s=='redshift' for s,_ in c.quotas) else []
