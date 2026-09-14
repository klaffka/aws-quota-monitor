"""AWS IoT TwinMaker workspace inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-3BCB51AD', 'Workspaces in this account in the current Region',
           lambda ctx: dict(usage=len(ctx.call('iottwinmaker', 'list_workspaces', 'workspaceSummaries')),
                            source='iottwinmaker:ListWorkspaces', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_twinmaker(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iottwinmaker' for service, _ in context.quotas): return []
    return context.run('iottwinmaker', CHECKS, skip)
