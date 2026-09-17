"""Amazon DocumentDB regional resource inventories and per-parent scopes.

`Tags per resource` stays in the audit: every cluster, instance, snapshot,
subnet group and parameter group would have to be read for its tags, and the
maximum could sit on any one of them.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DOCDB = 'docdb'


def count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call(DOCDB, method, key, **kwargs)),
                source=f'docdb:{method}', method='ACCOUNT_COUNT')


def _identified(ctx, method, key, field, subject):
    for entry in ctx.call(DOCDB, method, key):
        identity = entry.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'DocumentDB {subject} is missing its identity')
        yield identity, entry


def read_replicas_per_cluster(ctx):
    """Every cluster has exactly one writer, which is not a read replica."""
    return maximum([(identity,
                     sum(not member.get('IsClusterWriter')
                         for member in entry.get('DBClusterMembers') or ()), None)
                    for identity, entry in _identified(ctx, 'describe_db_clusters',
                                                       'DBClusters', 'DBClusterIdentifier',
                                                       'cluster')],
                   'DocDBCluster', 'docdb:DescribeDBClusters')


def subnets_per_subnet_group(ctx):
    return maximum([(identity, len(entry.get('Subnets') or ()), None)
                    for identity, entry in _identified(ctx, 'describe_db_subnet_groups',
                                                       'DBSubnetGroups', 'DBSubnetGroupName',
                                                       'subnet group')],
                   'DocDBSubnetGroup', 'docdb:DescribeDBSubnetGroups')


def security_groups_per_instance(ctx):
    return maximum([(identity, len(entry.get('VpcSecurityGroups') or ()), None)
                    for identity, entry in _identified(ctx, 'describe_db_instances',
                                                       'DBInstances', 'DBInstanceIdentifier',
                                                       'instance')],
                   'DocDBInstance', 'docdb:DescribeDBInstances')


CHECKS = [
    ('L-13F31459', 'Clusters', lambda ctx: count(ctx, 'describe_db_clusters', 'DBClusters')),
    ('L-739A3A85', 'Instances', lambda ctx: count(ctx, 'describe_db_instances', 'DBInstances')),
    ('L-02DEA053', 'Subnet groups', lambda ctx: count(ctx, 'describe_db_subnet_groups', 'DBSubnetGroups')),
    ('L-2A542E16', 'Cluster parameter groups',
     lambda ctx: count(ctx, 'describe_db_cluster_parameter_groups', 'DBClusterParameterGroups')),
    ('L-F7FABF71', 'Event subscriptions',
     lambda ctx: count(ctx, 'describe_event_subscriptions', 'EventSubscriptionsList')),
    # Automated snapshots hold a different quota, so AWS filters them out here.
    ('L-B2551F83', 'Manual cluster snapshots',
     lambda ctx: count(ctx, 'describe_db_cluster_snapshots', 'DBClusterSnapshots',
                       SnapshotType='manual')),
    ('L-5BA57179', 'Read replicas per cluster', read_replicas_per_cluster),
    ('L-36C7F3F8', 'Subnets per subnet group', subnets_per_subnet_group),
    ('L-D02D85EA', 'VPC security groups per instance', security_groups_per_instance),
]


def get_current_quotastatus_docdb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'docdb' for service, _ in context.quotas): return []
    return context.run('docdb', CHECKS, skip)
