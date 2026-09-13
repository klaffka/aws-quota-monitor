"""Amazon EventBridge Scheduler regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('scheduler', method, key)), source=f'scheduler:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-EE5D6FF0', 'Number of schedules', lambda ctx: resource_count(ctx, 'list_schedules', 'Schedules')),
    ('L-A632CD40', 'Number of schedule groups', lambda ctx: resource_count(ctx, 'list_schedule_groups', 'ScheduleGroups')),
]


def get_current_quotastatus_scheduler(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'scheduler' for service, _ in context.quotas):
        return []
    return context.run('scheduler', CHECKS, skip)
