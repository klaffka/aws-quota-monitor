"""Amazon EMR active-cluster inventory."""
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.aws import maximum


def active_instances_per_instance_group(ctx):
    values = []
    for cluster in ctx.call('elasticmapreduce', 'list_clusters', 'Clusters'):
        cluster_id = cluster.get('Id')
        if not cluster_id:
            continue
        for group in ctx.call('elasticmapreduce', 'list_instance_groups', 'InstanceGroups', ClusterId=cluster_id):
            group_id = group.get('Id')
            running = group.get('RunningInstanceCount', 0)
            if group_id:
                values.append((group_id, running, None))
    return maximum(values, 'InstanceGroup', 'elasticmapreduce:ListInstanceGroups')


CHECKS = [
    ('L-1EE7982C', 'Maximum number of active clusters',
     lambda ctx: dict(usage=len(ctx.call('elasticmapreduce', 'list_clusters', 'Clusters',
                                         ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING', 'TERMINATING'])),
                      source='elasticmapreduce:ListClusters', method='ACCOUNT_COUNT')),
    ('L-77B909B1', 'Active instances per instance group', active_instances_per_instance_group),
]


def get_current_quotastatus_emr(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'elasticmapreduce' for service, _ in context.quotas):
        return []
    return context.run('elasticmapreduce', CHECKS, skip)
