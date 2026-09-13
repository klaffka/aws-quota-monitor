"""AWS Proton regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-1C8983C3', 'Services per account',
     lambda c: dict(usage=len(c.call('proton', 'list_services', 'services')),
                    source='proton:ListServices', method='ACCOUNT_COUNT')),
    ('L-37A692EA', 'Environments per account',
     lambda c: dict(usage=len(c.call('proton', 'list_environments', 'environments')),
                    source='proton:ListEnvironments', method='ACCOUNT_COUNT')),
    ('L-405DC02B', 'Templates per account',
     lambda c: dict(usage=len(c.call('proton', 'list_service_templates', 'templates')),
                    source='proton:ListServiceTemplates', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_proton(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'proton' for service, _ in context.quotas):
        return []
    return context.run('proton', CHECKS, skip)
