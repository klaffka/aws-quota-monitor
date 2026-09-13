"""Amazon GameLift Streams regional resource counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-C9680889', 'Applications',
     lambda c: dict(usage=len(c.call('gameliftstreams', 'list_applications', 'Items')),
                    source='gameliftstreams:ListApplications', method='ACCOUNT_COUNT')),
    ('L-E84C6A80', 'Stream groups',
     lambda c: dict(usage=len(c.call('gameliftstreams', 'list_stream_groups', 'Items')),
                    source='gameliftstreams:ListStreamGroups', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_gameliftstreams(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'gameliftstreams' for service, _ in context.quotas):
        return []
    return context.run('gameliftstreams', CHECKS, skip)
