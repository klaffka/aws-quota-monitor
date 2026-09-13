"""AWS Systems Manager Incident Manager Contacts resource counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-7DD2017D', 'Contacts per account', lambda c: dict(usage=len(c.call('ssm-contacts', 'list_contacts', 'Contacts')), source='ssm-contacts:ListContacts', method='ACCOUNT_COUNT')),
    ('L-4EA3AB3A', 'Rotations per account', lambda c: dict(usage=len(c.call('ssm-contacts', 'list_rotations', 'Rotations')), source='ssm-contacts:ListRotations', method='ACCOUNT_COUNT')),
]

def get_current_quotastatus_ssm_contacts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ssm-contacts' for service, _ in context.quotas): return []
    return context.run('ssm-contacts', CHECKS, skip)
