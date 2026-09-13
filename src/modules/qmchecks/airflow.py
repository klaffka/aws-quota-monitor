"""Amazon MWAA environment inventory for the Service Quotas ``airflow`` code."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-67D41C6B', 'Environments per account per Region',
     lambda c: dict(usage=len(c.call('mwaa', 'list_environments', 'Environments')),
                    source='mwaa:ListEnvironments', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_airflow(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'airflow' for service, _ in context.quotas):
        return []
    return context.run('airflow', CHECKS, skip)
