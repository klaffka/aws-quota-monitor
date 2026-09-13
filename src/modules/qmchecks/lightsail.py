"""Amazon Lightsail regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('lightsail', method, key)), source=f'lightsail:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-4259AF9B', 'Instances', lambda ctx: count(ctx, 'get_instances', 'instances')),
    ('L-3B2B13A1', 'Databases', lambda ctx: count(ctx, 'get_relational_databases', 'relationalDatabases')),
    ('L-BB561519', 'Container services', lambda ctx: count(ctx, 'get_container_services', 'containerServices')),
]


def get_current_quotastatus_lightsail(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'lightsail' for service, _ in context.quotas): return []
    return context.run('lightsail', CHECKS, skip)
