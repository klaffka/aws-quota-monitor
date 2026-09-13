"""Amazon DocumentDB elastic cluster counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-B3699347', 'Elastic clusters',
           lambda c: dict(usage=len(c.call('docdb-elastic', 'list_clusters', 'clusters')),
                          source='docdb-elastic:ListClusters', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_docdb_elastic(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'docdb-elastic' for service, _ in context.quotas): return []
    return context.run('docdb-elastic', CHECKS, skip)
