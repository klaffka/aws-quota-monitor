"""AWS Deadline Cloud farm, fleet, queue and association quotas.

The step, task and job member quotas would need a walk through every job in
every queue, which a render farm makes unbounded, and the regional vCPU and GPU
quotas aggregate fleet capacity that the worker listing does not report.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DEADLINE = 'deadline'


def _identity(item, field, subject):
    value = item.get(field) or item.get('id')
    if not isinstance(value, str) or not value:
        raise NoData(f'Deadline {subject} is missing its identity')
    return value


def farms(ctx):
    return [_identity(farm, 'farmId', 'farm')
            for farm in ctx.call(DEADLINE, 'list_farms', 'farms')]


def fleets(farm, ctx):
    return [_identity(fleet, 'fleetId', 'fleet')
            for fleet in ctx.call(DEADLINE, 'list_fleets', 'fleets', farmId=farm)]


def queues(farm, ctx):
    return [_identity(queue, 'queueId', 'queue')
            for queue in ctx.call(DEADLINE, 'list_queues', 'queues', farmId=farm)]


def account_count(ctx, method, key):
    return dict(usage=len(ctx.call(DEADLINE, method, key)),
                source=f'deadline:{method}', method='ACCOUNT_COUNT')


def per_farm(ctx, method, key):
    values = []
    for farm in farms(ctx):
        resources = ctx.call(DEADLINE, method, key, farmId=farm)
        values.append((farm, len(resources), None))
    return maximum(values, 'DeadlineFarm', f'deadline:{method}')


def _per_farm_children(method, key, children, argument):
    """Sum a per-child listing back up to the farm that owns it."""
    def check(ctx):
        values = []
        for farm in farms(ctx):
            usage = sum(len(ctx.call(DEADLINE, method, key, farmId=farm,
                                     **{argument: child}))
                        for child in children(farm, ctx))
            values.append((farm, usage, None))
        return maximum(values, 'DeadlineFarm', f'deadline:{method}')
    return check


def _per_child(method, key, children, argument, resource_type):
    def check(ctx):
        values = []
        for farm in farms(ctx):
            for child in children(farm, ctx):
                entries = ctx.call(DEADLINE, method, key, farmId=farm,
                                   **{argument: child})
                values.append((f'{farm}/{child}', len(entries), None))
        return maximum(values, resource_type, f'deadline:{method}')
    return check


def queue_limit_associations_per_queue(ctx):
    """The farm-wide listing carries the queue each association belongs to."""
    values = []
    for farm in farms(ctx):
        counts = Counter({f'{farm}/{queue}': 0 for queue in queues(farm, ctx)})
        for association in ctx.call(DEADLINE, 'list_queue_limit_associations',
                                    'queueLimitAssociations', farmId=farm):
            queue = association.get('queueId')
            if not isinstance(queue, str) or not queue:
                raise NoData('Deadline queue limit association names no queue')
            counts[f'{farm}/{queue}'] += 1
        values.extend((queue, count, None) for queue, count in counts.items())
    return maximum(values, 'DeadlineQueue', 'deadline:ListQueueLimitAssociations')


CHECKS = [
    ('L-2DEF7E07', 'Farms per region',
     lambda ctx: account_count(ctx, 'list_farms', 'farms')),
    ('L-F4ED6ADC', 'Monitors per region',
     lambda ctx: account_count(ctx, 'list_monitors', 'monitors')),
    ('L-F0DF6BC2', 'License endpoints per region',
     lambda ctx: account_count(ctx, 'list_license_endpoints', 'licenseEndpoints')),
    ('L-55A8E463', 'Fleets per farm', lambda ctx: per_farm(ctx, 'list_fleets', 'fleets')),
    ('L-5E4FD3A4', 'Queues per farm', lambda ctx: per_farm(ctx, 'list_queues', 'queues')),
    ('L-48CC9B8E', 'Workers per farm',
     _per_farm_children('list_workers', 'workers', fleets, 'fleetId')),
    ('L-5369B22C', 'Jobs per farm',
     _per_farm_children('list_jobs', 'jobs', queues, 'queueId')),
    ('L-86C1F13E', 'Budgets per farm',
     lambda ctx: per_farm(ctx, 'list_budgets', 'budgets')),
    ('L-8148A0DC', 'Storage profiles per farm',
     lambda ctx: per_farm(ctx, 'list_storage_profiles', 'storageProfiles')),
    ('L-253A82CE', 'Limits per farm', lambda ctx: per_farm(ctx, 'list_limits', 'limits')),
    ('L-BF011D88', 'Queue fleet associations per farm',
     lambda ctx: per_farm(ctx, 'list_queue_fleet_associations',
                          'queueFleetAssociations')),
    ('L-2F4AD227', 'Associated members per farm',
     lambda ctx: per_farm(ctx, 'list_farm_members', 'members')),
    ('L-D7E39278', 'Associated members per fleet',
     _per_child('list_fleet_members', 'members', fleets, 'fleetId', 'DeadlineFleet')),
    ('L-B1CBF582', 'Associated members per queue',
     _per_child('list_queue_members', 'members', queues, 'queueId', 'DeadlineQueue')),
    ('L-162A55BC', 'Queue environments per queue',
     _per_child('list_queue_environments', 'environments', queues, 'queueId',
                'DeadlineQueue')),
    ('L-55B7030C', 'Queue limit associations per queue',
     queue_limit_associations_per_queue),
]


def get_current_quotastatus_deadline(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'deadline' for service, _ in context.quotas):
        return []
    return context.run('deadline', CHECKS, skip)
