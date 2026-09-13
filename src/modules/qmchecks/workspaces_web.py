"""Amazon WorkSpaces Web resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def count(method, key):
    return lambda c: dict(usage=len(c.call('workspaces-web', method, key)),
                          source=f'workspaces-web:{method}', method='ACCOUNT_COUNT')


def per_parent(c, parent_method, parent_key, child_method, child_key, parent_arg, kind):
    values = []
    for parent in c.call('workspaces-web', parent_method, parent_key):
        arn = parent.get('portalArn') or parent.get('trustStoreArn')
        values.append((arn, len(c.call('workspaces-web', child_method, child_key, **{parent_arg: arn})), None))
    return maximum(values, kind, f'workspaces-web:{child_method}')


CHECKS = [
    ('L-149BA3AD', 'Number of Portals', count('list_portals', 'portals')),
    ('L-3A76276F', 'Number of TrustStores', count('list_trust_stores', 'trustStores')),
    ('L-36965BD1', 'Number of BrowserSettings', count('list_browser_settings', 'browserSettings')),
    ('L-3A62D5A9', 'Number of UserSettings', count('list_user_settings', 'userSettings')),
    ('L-787608AB', 'Number of NetworkSettings', count('list_network_settings', 'networkSettings')),
    ('L-78A0B046', 'Number of IpAccessSettings', count('list_ip_access_settings', 'ipAccessSettings')),
    ('L-122C6700', 'Number of DataProtectionSettings', count('list_data_protection_settings', 'dataProtectionSettings')),
    ('L-21C7999E', 'Number of SessionLoggers', count('list_session_loggers', 'sessionLoggers')),
    ('L-8BD59015', 'Number of UserAccessLoggingSettings', count('list_user_access_logging_settings', 'userAccessLoggingSettings')),
    ('L-DFC864EF', 'Number of IdentityProviders per Portal',
     lambda c: per_parent(c, 'list_portals', 'portals', 'list_identity_providers', 'identityProviders', 'portalArn', 'Portal')),
    ('L-B30615E2', 'Number of Certificates per TrustStore',
     lambda c: per_parent(c, 'list_trust_stores', 'trustStores', 'list_trust_store_certificates', 'certificateList', 'trustStoreArn', 'TrustStore')),
]


def get_current_quotastatus_workspaces_web(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'workspaces-web' for service, _ in context.quotas):
        return []
    return context.run('workspaces-web', CHECKS, skip)
