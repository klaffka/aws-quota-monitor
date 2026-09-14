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


CHECKS = [
    ('L-CFEB8E8D', 'Registered repositories',
     lambda ctx: dict(usage=len(repositories(ctx)), source='ecr:DescribeRepositories',
                      method='ACCOUNT_COUNT')),
    ('L-03A36CE1', 'Images per repository', images_per_repository),
    ('L-6EF7FC96', 'Pull-through cache rules per registry',
     lambda ctx: dict(usage=len(ctx.call('ecr', 'describe_pull_through_cache_rules',
                                         'pullThroughCacheRules', registryId=ctx.account)),
                      source='ecr:DescribePullThroughCacheRules', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_ecr(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ecr' for service, _ in context.quotas):
        return []
    return context.run('ecr', CHECKS, skip)
