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


# DescribeServices takes at most ten services and DescribeClusters a hundred.
SERVICE_BATCH = 10
CLUSTER_BATCH = 100


def _batched(items, size):
    items = list(items)
    for start in range(0, len(items), size):
        yield items[start:start + size]


def described_clusters(ctx):
    for batch in _batched(clusters(ctx), CLUSTER_BATCH):
        yield from ctx.call('ecs', 'describe_clusters', 'clusters', clusters=batch)


def described_services(ctx):
    """Yield every service's detail, one cluster and one batch at a time."""
    for cluster in clusters(ctx):
        arns = ctx.call('ecs', 'list_services', 'serviceArns', cluster=cluster)
        for batch in _batched(arns, SERVICE_BATCH):
            yield from ctx.call('ecs', 'describe_services', 'services',
                                cluster=cluster, services=batch)


def capacity_providers_per_cluster(ctx):
    return maximum([(cluster.get('clusterArn'), len(cluster.get('capacityProviders') or ()), None)
                    for cluster in described_clusters(ctx)],
                   'ECSCluster', 'ecs:DescribeClusters')


def _load_balancers_per_service(ctx, field):
    return maximum([(service.get('serviceArn'),
                     sum(bool(balancer.get(field)) for balancer in service.get('loadBalancers') or ()),
                     None)
                    for service in described_services(ctx)],
                   'ECSService', 'ecs:DescribeServices')


def tasks_per_service(ctx):
    """Take the larger of the running and desired counts.

    A service scaling up runs fewer tasks than it has asked for, and the quota
    has to accommodate what it asked for, so the smaller number would understate
    the usage for exactly as long as the deployment lasts.
    """
    return maximum([(service.get('serviceArn'),
                     max(service.get('runningCount') or 0, service.get('desiredCount') or 0),
                     None)
                    for service in described_services(ctx)],
                   'ECSService', 'ecs:DescribeServices')


CHECKS = [
    ('L-A24B7D58', 'Capacity providers per cluster', capacity_providers_per_cluster),
    ('L-A04A77EF', 'Target groups per service',
     lambda ctx: _load_balancers_per_service(ctx, 'targetGroupArn')),
    ('L-E4A1E1D7', 'Classic Load Balancers per service',
     lambda ctx: _load_balancers_per_service(ctx, 'loadBalancerName')),
    ('L-92E49DE3', 'Tasks per service', tasks_per_service),
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
