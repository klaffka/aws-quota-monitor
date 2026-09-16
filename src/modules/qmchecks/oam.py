"""AWS CloudWatch Observability Access Manager resource counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-92C40D6D', 'Number of links',
     lambda c: dict(usage=len(c.call('oam', 'list_links', 'Items')),
                    source='oam:ListLinks', method='ACCOUNT_COUNT')),
    ('L-AA726EB1', 'Number of sinks',
     lambda c: dict(usage=len(c.call('oam', 'list_sinks', 'Items')),
                    source='oam:ListSinks', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_oam(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'oam' for service, _ in context.quotas):
        return []
    return context.run('oam', CHECKS, skip)
