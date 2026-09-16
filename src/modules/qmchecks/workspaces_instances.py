"""WorkSpaces Managed Instances regional counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-7D173EC3', 'WorkSpaces Managed Instances',
           lambda c: dict(usage=len(c.call('workspaces-instances', 'list_workspace_instances', 'WorkspaceInstances')),
                          source='workspaces-instances:ListWorkspaceInstances', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_workspaces_instances(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'workspaces-instances' for service, _ in context.quotas): return []
    return context.run('workspaces-instances', CHECKS, skip)
