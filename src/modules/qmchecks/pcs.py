"""Amazon ParallelCluster Service regional cluster counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-0ADE95E3', 'Clusters',
     lambda c: dict(usage=len(c.call('pcs', 'list_clusters', 'clusters')),
                    source='pcs:ListClusters', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_pcs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'pcs' for service, _ in context.quotas):
        return []
    return context.run('pcs', CHECKS, skip)
