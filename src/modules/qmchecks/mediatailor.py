"""AWS Elemental MediaTailor regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('mediatailor', method, key)), source=f'mediatailor:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-2290981E', 'Source Locations', lambda ctx: count(ctx, 'list_source_locations', 'Items')),
    ('L-29DF1B92', 'Channels per account', lambda ctx: count(ctx, 'list_channels', 'Items')),
]


def get_current_quotastatus_mediatailor(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediatailor' for service, _ in context.quotas): return []
    return context.run('mediatailor', CHECKS, skip)
