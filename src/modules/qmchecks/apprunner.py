"""AWS App Runner regional service inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-69F96A0C', 'Services',
           lambda ctx: dict(usage=len(ctx.call('apprunner', 'list_services', 'ServiceSummaryList')),
                            source='apprunner:ListServices', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_apprunner(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'apprunner' for service, _ in context.quotas): return []
    return context.run('apprunner', CHECKS, skip)
