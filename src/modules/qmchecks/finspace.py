"""AWS FinSpace kdb environment inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-C49840B4', 'Total kdb environments',
           lambda ctx: dict(usage=len(ctx.call('finspace', 'list_kx_environments', 'environments')),
                            source='finspace:ListKxEnvironments', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_finspace(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'finspace' for service, _ in context.quotas): return []
    return context.run('finspace', CHECKS, skip)
