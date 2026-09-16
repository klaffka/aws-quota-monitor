"""AWS Application Discovery Service imported-server counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-E92F1B88', 'Imported servers per account',
           lambda c: dict(usage=len(c.call('discovery', 'list_configurations', 'configurations', configurationType='SERVER')),
                          source='discovery:ListConfigurations', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_discovery(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'discovery' for service, _ in context.quotas): return []
    return context.run('discovery', CHECKS, skip)
