"""ElastiCache regional subnet-group inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(method, key):
    return lambda ctx: dict(usage=len(ctx.call('elasticache', method, key)),
                            source=f'elasticache:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-3E7F7726', 'Subnet groups per Region', count('describe_cache_subnet_groups', 'CacheSubnetGroups')),
    ('L-80E085C7', 'Users per Region', count('describe_users', 'Users')),
    ('L-3F15A733', 'Parameter groups per Region', count('describe_cache_parameter_groups', 'CacheParameterGroups')),
    ('L-AD484FC5', 'User Groups per Region', count('describe_user_groups', 'UserGroups')),
    ('L-BBCDAECC', 'Serverless Caches per Region', count('describe_serverless_caches', 'ServerlessCaches')),
]


def get_current_quotastatus_elasticache(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'elasticache' for service, _ in context.quotas): return []
    return context.run('elasticache', CHECKS, skip)
