"""Amazon SES regional tenant resource quota."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-E7F21B4C', 'Tenant count',
     lambda ctx: dict(usage=len(ctx.call('sesv2', 'list_tenants', 'Tenants')),
                      source='sesv2:ListTenants', method='ACCOUNT_COUNT')),
    ('L-10E24536', 'Configuration set count',
     lambda ctx: dict(usage=len(ctx.call('ses', 'list_configuration_sets', 'ConfigurationSets')),
                      source='ses:ListConfigurationSets', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_ses(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ses' for service, _ in context.quotas):
        return []
    return context.run('ses', CHECKS, skip)
