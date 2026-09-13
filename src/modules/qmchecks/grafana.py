"""Amazon Managed Grafana regional workspace counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-2C2D5119', 'Number of workspaces',
     lambda c: dict(usage=len(c.call('grafana', 'list_workspaces', 'workspaces')),
                    source='grafana:ListWorkspaces', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_grafana(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'grafana' for service, _ in context.quotas):
        return []
    return context.run('grafana', CHECKS, skip)
