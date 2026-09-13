"""AWS Data Exchange regional data-set counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-52E2E63A', 'Data sets per account', lambda c: dict(usage=len(c.call('dataexchange', 'list_data_sets', 'DataSets')), source='dataexchange:ListDataSets', method='ACCOUNT_COUNT')),
    ('L-8EB7960E', 'Event actions per account', lambda c: dict(usage=len(c.call('dataexchange', 'list_event_actions', 'EventActions')), source='dataexchange:ListEventActions', method='ACCOUNT_COUNT')),
]

def get_current_quotastatus_dataexchange(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dataexchange' for service, _ in context.quotas): return []
    return context.run('dataexchange', CHECKS, skip)
