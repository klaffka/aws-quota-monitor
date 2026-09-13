"""Amazon ECS regional inventory checks."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def clusters(ctx):
    return ctx.call('ecs', 'list_clusters', 'clusterArns')


def services_per_cluster(ctx):
    values = []
    for cluster in clusters(ctx):
        services = ctx.call('ecs', 'list_services', 'serviceArns', cluster=cluster)
        values.append((cluster, len(services), None))
    return maximum(values, 'ECSCluster', 'ecs:ListServices')


def task_definition_families(ctx):
    return ctx.call('ecs', 'list_task_definition_families', 'families', status='ALL')


def revisions_per_family(ctx):
    values = []
    for family in task_definition_families(ctx):
        revisions = set()
        for status in ('ACTIVE', 'INACTIVE'):
            revisions.update(ctx.call('ecs', 'list_task_definitions', 'taskDefinitionArns',
                                      familyPrefix=family, status=status))
        values.append((family, len(revisions), None))
    return maximum(values, 'TaskDefinitionFamily', 'ecs:ListTaskDefinitions')


def container_instances_per_cluster(ctx):
    values = []
    for cluster in clusters(ctx):
        values.append((cluster, len(ctx.call('ecs', 'list_container_instances', 'containerInstanceArns', cluster=cluster)), None))
    return maximum(values, 'ECSCluster', 'ecs:ListContainerInstances')


CHECKS = [
    ('L-21C621EB', 'Clusters per account',
     lambda ctx: dict(usage=len(clusters(ctx)), source='ecs:ListClusters', method='ACCOUNT_COUNT')),
    ('L-9EF96962', 'Services per cluster', services_per_cluster),
    ('L-B9151B48', 'Revisions per task definition family', revisions_per_family),
    ('L-86C34207', 'Container instances per cluster', container_instances_per_cluster),
]


def get_current_quotastatus_ecs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ecs' for service, _ in context.quotas):
        return []
    return context.run('ecs', CHECKS, skip)
