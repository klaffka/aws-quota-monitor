"""Amazon EventBridge regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('events', method, key)),
                source=f'events:{method}', method='ACCOUNT_COUNT')


def targets_per_rule(ctx):
    values = []
    for rule in ctx.call('events', 'list_rules', 'Rules'):
        name = rule.get('Name')
        if name:
            values.append((name, len(ctx.call('events', 'list_targets_by_rule', 'Targets', RuleName=name)), None))
    return maximum(values, 'EventBridgeRule', 'events:ListTargetsByRule')


CHECKS = [
    ('L-658A4FD9', 'Event buses',
     lambda ctx: resource_count(ctx, 'list_event_buses', 'EventBuses')),
    ('L-244521F2', 'Number of rules',
     lambda ctx: resource_count(ctx, 'list_rules', 'Rules')),
    ('L-388D1D08', 'Targets per rule', targets_per_rule),
]


def get_current_quotastatus_eventbridge(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'events' for service, _ in context.quotas):
        return []
    return context.run('events', CHECKS, skip)
