"""Amazon ECR quotas backed by the regional repository inventory."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def repositories(ctx):
    return ctx.call('ecr', 'describe_repositories', 'repositories', registryId=ctx.account)


def images_per_repository(ctx):
    values = []
    for repository in repositories(ctx):
        name = repository.get('repositoryName')
        if name:
            values.append((name, len(ctx.call('ecr', 'describe_images', 'imageDetails',
                                               registryId=ctx.account,
                                               repositoryName=name)), None))
    return maximum(values, 'ECRRepository', 'ecr:DescribeRepositories+DescribeImages')


def _replication_rules(ctx):
    """One DescribeRegistry call answers all three replication quotas."""
    registry = ctx.call('ecr', 'describe_registry')
    configuration = registry.get('replicationConfiguration') or {}
    return configuration.get('rules') or []


def replication_rules(ctx):
    return dict(usage=len(_replication_rules(ctx)),
                source='ecr:DescribeRegistry', method='ACCOUNT_COUNT')


def filters_per_replication_rule(ctx):
    return maximum([(f'rule-{index}', len(rule.get('repositoryFilters') or ()), None)
                    for index, rule in enumerate(_replication_rules(ctx))],
                   'ECRReplicationRule', 'ecr:DescribeRegistry')


def replication_destinations(ctx):
    """A region named by two rules is still one destination."""
    destinations = set()
    for rule in _replication_rules(ctx):
        for destination in rule.get('destinations') or ():
            destinations.add((destination.get('region'), destination.get('registryId')))
    return dict(usage=len(destinations), source='ecr:DescribeRegistry',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-CFEB8E8D', 'Registered repositories',
     lambda ctx: dict(usage=len(repositories(ctx)), source='ecr:DescribeRepositories',
                      method='ACCOUNT_COUNT')),
    ('L-03A36CE1', 'Images per repository', images_per_repository),
    ('L-6EF7FC96', 'Pull-through cache rules per registry',
     lambda ctx: dict(usage=len(ctx.call('ecr', 'describe_pull_through_cache_rules',
                                         'pullThroughCacheRules', registryId=ctx.account)),
                      source='ecr:DescribePullThroughCacheRules', method='ACCOUNT_COUNT')),
    ('L-9B60BFFB', 'Rules per replication configuration', replication_rules),
    ('L-241DEEBA', 'Filters per rule in a replication configuration',
     filters_per_replication_rule),
    ('L-24725E9A', 'Unique destinations across all rules in a replication configuration',
     replication_destinations),
]


def get_current_quotastatus_ecr(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ecr' for service, _ in context.quotas):
        return []
    return context.run('ecr', CHECKS, skip)
