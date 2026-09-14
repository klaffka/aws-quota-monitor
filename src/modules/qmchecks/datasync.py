"""AWS DataSync task inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-74E04279', 'Tasks',
     lambda ctx: dict(usage=len(ctx.call('datasync', 'list_tasks', 'Tasks')),
                      source='datasync:ListTasks', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_datasync(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'datasync' for service, _ in context.quotas):
        return []
    return context.run('datasync', CHECKS, skip)
