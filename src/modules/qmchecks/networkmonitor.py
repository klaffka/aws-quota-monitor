"""Amazon CloudWatch Network Monitor regional monitor counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-A4298AB9', 'Number of monitors per account per AWS Region',
     lambda c: dict(usage=len(c.call('networkmonitor', 'list_monitors', 'monitors')),
                    source='networkmonitor:ListMonitors', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_networkmonitor(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'networkmonitor' for service, _ in context.quotas):
        return []
    return context.run('networkmonitor', CHECKS, skip)
