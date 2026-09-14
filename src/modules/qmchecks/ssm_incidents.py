"""SSM Incident Manager replication-set counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-39562D83', 'Replication sets per account',
           lambda c: dict(usage=len(c.call('ssm-incidents', 'list_replication_sets', 'replicationSetArns')),
                          source='ssm-incidents:ListReplicationSets', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_ssm_incidents(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ssm-incidents' for service, _ in context.quotas): return []
    return context.run('ssm-incidents', CHECKS, skip)
