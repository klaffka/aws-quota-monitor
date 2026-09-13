"""Amazon DocumentDB regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('docdb', method, key)), source=f'docdb:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-13F31459', 'Clusters', lambda ctx: count(ctx, 'describe_db_clusters', 'DBClusters')),
    ('L-739A3A85', 'Instances', lambda ctx: count(ctx, 'describe_db_instances', 'DBInstances')),
    ('L-02DEA053', 'Subnet groups', lambda ctx: count(ctx, 'describe_db_subnet_groups', 'DBSubnetGroups')),
]


def get_current_quotastatus_docdb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'docdb' for service, _ in context.quotas): return []
    return context.run('docdb', CHECKS, skip)
