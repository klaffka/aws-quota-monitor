"""Amazon CloudWatch RUM app monitor inventory."""
from modules.qmcore.aws import CheckContext, session_from_env

RUM = 'rum'

CHECKS = [
    ('L-3FB7EA17', 'RUM AppMonitors',
     lambda ctx: dict(usage=len(ctx.call(RUM, 'list_app_monitors',
                                         'AppMonitorSummaries')),
                      source='rum:ListAppMonitors', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_rum(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rum' for service, _ in context.quotas):
        return []
    return context.run('rum', CHECKS, skip)
