"""Amazon Aurora DSQL regional cluster counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-B3A4E51E', 'Single-Region clusters',
     lambda c: dict(usage=len(c.call('dsql', 'list_clusters', 'clusters')),
                    source='dsql:ListClusters', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_dsql(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dsql' for service, _ in context.quotas):
        return []
    return context.run('dsql', CHECKS, skip)
