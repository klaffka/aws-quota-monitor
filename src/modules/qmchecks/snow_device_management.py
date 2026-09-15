"""AWS Snow Device Management task quotas."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

SNOW = 'snow-device-management'
TASK_STATES = {'IN_PROGRESS', 'CANCELED', 'COMPLETED'}
RUNNING_STATES = {'IN_PROGRESS'}


def tasks(ctx):
    found = {}
    for task in ctx.call(SNOW, 'list_tasks', 'tasks'):
        identity = task.get('taskId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Snow device task is missing its identity')
        if task.get('state') not in TASK_STATES:
            raise NoData('Snow device task has an unknown state')
        found[identity] = task
    return found


CHECKS = [
    ('L-D88A1E78', 'Snow Device Management maximum tasks.',
     lambda ctx: dict(usage=len(tasks(ctx)), source='snow-device-management:ListTasks',
                      method='ACCOUNT_COUNT')),
    ('L-FFEB0409', 'Snow Device Management active tasks.',
     lambda ctx: dict(usage=sum(task['state'] in RUNNING_STATES
                                for task in tasks(ctx).values()),
                      source='snow-device-management:ListTasks',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_snow_device_management(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    service = 'snow-device-management'
    if not any(code == service for code, _ in context.quotas):
        return []
    return context.run(service, CHECKS, skip)
