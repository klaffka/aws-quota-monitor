"""AWS Mainframe Modernization resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('m2', method, key)), source=f'm2:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-00464274', 'Max Applications Per AWS Account', lambda ctx: count(ctx, 'list_applications', 'applications')),
    ('L-6851C542', 'Max Environments Per AWS Account', lambda ctx: count(ctx, 'list_environments', 'environments')),
]


def get_current_quotastatus_m2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'm2' for service, _ in context.quotas): return []
    return context.run('m2', CHECKS, skip)
