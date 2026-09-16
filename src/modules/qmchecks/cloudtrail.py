"""CloudTrail regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('cloudtrail', method, key)),
                source=f'cloudtrail:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-1568E18E', 'Trails per region',
     lambda ctx: resource_count(ctx, 'describe_trails', 'trailList')),
    ('L-FAC66D2D', 'Event data stores',
     lambda ctx: resource_count(ctx, 'list_event_data_stores', 'EventDataStores')),
    ('L-422D51DD', 'Channels',
     lambda ctx: resource_count(ctx, 'list_channels', 'Channels')),
    ('L-F5FAD268', 'Custom dashboards per region',
     lambda ctx: resource_count(ctx, 'list_dashboards', 'Dashboards')),
]


def get_current_quotastatus_cloudtrail(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cloudtrail' for service, _ in context.quotas):
        return []
    return context.run('cloudtrail', CHECKS, skip)
