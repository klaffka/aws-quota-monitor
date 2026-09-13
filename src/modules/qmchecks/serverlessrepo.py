"""AWS Serverless Application Repository application counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-38772E7B', 'Public applications',
     lambda c: dict(usage=len(c.call('serverlessrepo', 'list_applications', 'Applications')),
                    source='serverlessrepo:ListApplications', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_serverlessrepo(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'serverlessrepo' for service, _ in context.quotas):
        return []
    return context.run('serverlessrepo', CHECKS, skip)
