"""CloudTrail regional resource counts and per-trail selector scopes.

One GetEventSelectors call per trail answers all three selector quotas, so the
trails are walked once however many of them are asked for.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('cloudtrail', method, key)),
                source=f'cloudtrail:{method}', method='ACCOUNT_COUNT')


def _selectors(ctx):
    """Yield (trail, its selector answer) for every trail in the Region."""
    for trail in ctx.call('cloudtrail', 'describe_trails', 'trailList'):
        name = trail.get('Name')
        if not isinstance(name, str) or not name:
            raise NoData('CloudTrail trail is missing its name')
        yield name, ctx.call('cloudtrail', 'get_event_selectors', TrailName=name)


def event_selectors(ctx):
    return maximum([(name, len(answer.get('EventSelectors') or ()), None)
                    for name, answer in _selectors(ctx)],
                   'CloudTrailTrail', 'cloudtrail:GetEventSelectors')


def data_resources_per_trail(ctx):
    """The quota bounds the resources across a trail's selectors, not one of them."""
    return maximum([(name, sum(len(selector.get('DataResources') or ())
                               for selector in answer.get('EventSelectors') or ()), None)
                    for name, answer in _selectors(ctx)],
                   'CloudTrailTrail', 'cloudtrail:GetEventSelectors')


def advanced_conditions_per_trail(ctx):
    return maximum([(name, sum(len(selector.get('FieldSelectors') or ())
                               for selector in answer.get('AdvancedEventSelectors') or ()), None)
                    for name, answer in _selectors(ctx)],
                   'CloudTrailTrail', 'cloudtrail:GetEventSelectors')


CHECKS = [
    ('L-1568E18E', 'Trails per region',
     lambda ctx: resource_count(ctx, 'describe_trails', 'trailList')),
    ('L-FAC66D2D', 'Event data stores',
     lambda ctx: resource_count(ctx, 'list_event_data_stores', 'EventDataStores')),
    ('L-422D51DD', 'Channels',
     lambda ctx: resource_count(ctx, 'list_channels', 'Channels')),
    ('L-F5FAD268', 'Custom dashboards per region',
     lambda ctx: resource_count(ctx, 'list_dashboards', 'Dashboards')),
    ('L-9387CED7', 'Event selectors', event_selectors),
    ('L-71DEA5C6', 'Data resources across all event selectors in a trail',
     data_resources_per_trail),
    ('L-203ED99D', 'Conditions across all advanced event selectors',
     advanced_conditions_per_trail),
]


def get_current_quotastatus_cloudtrail(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cloudtrail' for service, _ in context.quotas):
        return []
    return context.run('cloudtrail', CHECKS, skip)
