"""AWS Transfer Family regional account resource quotas.

The remaining quotas count traffic rather than configuration: concurrent AS2
messages on a server or connector, multiplexed SFTP sessions on a connection
and concurrent sessions on a server all exist only while a transfer is in
flight, and `Maximum number of new executions per workflow` bounds how fast
executions may start. Web app units are different, and are measured: they are
provisioned capacity that `DescribeWebApp` reports back.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('transfer', method, key)),
                source=f'transfer:{method}', method='ACCOUNT_COUNT')


def per_server(ctx, method, key):
    """Sum an inventory that is only listable per server, never per account."""
    usage = 0
    for server in ctx.call('transfer', 'list_servers', 'Servers'):
        server_id = server.get('ServerId')
        if server_id:
            usage += len(ctx.call('transfer', method, key, ServerId=server_id))
    return dict(usage=usage, source=f'transfer:ListServers+{method}', method='ACCOUNT_COUNT')


def vpc_endpoint_servers(ctx):
    servers = [server for server in ctx.call('transfer', 'list_servers', 'Servers')
               if server.get('EndpointType') == 'VPC_ENDPOINT']
    return dict(usage=len(servers), source='transfer:ListServers', method='ACCOUNT_COUNT')


def connectors_by_type(ctx, connector_type):
    return dict(usage=sum(c.get('ConnectorType') == connector_type
                          for c in ctx.call('transfer', 'list_connectors', 'Connectors')),
                source=f'transfer:ListConnectors(ConnectorType={connector_type})',
                method='ACCOUNT_COUNT')


def users_per_server(ctx):
    from modules.qmcore.aws import maximum
    values = []
    for server in ctx.call('transfer', 'list_servers', 'Servers'):
        sid = server.get('ServerId')
        users = ctx.call('transfer', 'list_users', 'Users', ServerId=sid)
        values.append((sid, len(users), None))
    return maximum(values, 'Server', 'transfer:ListUsers')


def logical_directory_mappings_per_user(ctx):
    from modules.qmcore.aws import maximum
    values = []
    for server in ctx.call('transfer', 'list_servers', 'Servers'):
        sid = server.get('ServerId')
        if not sid:
            continue
        for user in ctx.call('transfer', 'list_users', 'Users', ServerId=sid):
            name = user.get('UserName')
            if name:
                detail = ctx.call('transfer', 'describe_user', UserName=name, ServerId=sid)
                mappings = detail.get('User', {}).get('HomeDirectoryDetails', [])
                values.append((f'{sid}:{name}', len(mappings), None))
    return maximum(values, 'TransferUser', 'transfer:ListUsers+DescribeUser')


def certificates_per_profile(ctx):
    """The certificate listing does not say which profile holds a certificate."""
    from modules.qmcore.aws import maximum
    values = []
    for profile in ctx.call('transfer', 'list_profiles', 'Profiles'):
        identity = profile.get('ProfileId')
        if not identity:
            raise NoData('Transfer profile is missing its identity')
        detail = ctx.call('transfer', 'describe_profile', ProfileId=identity).get('Profile') or {}
        if detail.get('ProfileId') != identity:
            raise NoData('Transfer profile detail has a different identity')
        values.append((identity, len(detail.get('CertificateIds') or ()), None))
    return maximum(values, 'TransferProfile', 'transfer:ListProfiles+DescribeProfile')


def ssh_keys_per_service_managed_user(ctx):
    """Only a service-managed server holds users whose keys Transfer stores.

    ListUsers reports the key count directly, so no per-user detail is read.
    """
    from modules.qmcore.aws import maximum
    values = []
    for server in ctx.call('transfer', 'list_servers', 'Servers'):
        if server.get('IdentityProviderType') != 'SERVICE_MANAGED':
            continue
        server_id = server.get('ServerId')
        if not server_id:
            raise NoData('Transfer server is missing its identity')
        for user in ctx.call('transfer', 'list_users', 'Users', ServerId=server_id):
            name = user.get('UserName')
            keys = user.get('SshPublicKeyCount')
            if not name or not isinstance(keys, int):
                raise NoData('Transfer user has no name or no key count')
            values.append((f'{server_id}:{name}', keys, None))
    return maximum(values, 'TransferUser', 'transfer:ListServers+ListUsers')


def directory_accesses_per_server(ctx):
    """An access grants one directory group, so the accesses are the groups."""
    from modules.qmcore.aws import maximum
    values = []
    for server in ctx.call('transfer', 'list_servers', 'Servers'):
        if server.get('IdentityProviderType') != 'AWS_DIRECTORY_SERVICE':
            continue
        server_id = server.get('ServerId')
        if not server_id:
            raise NoData('Transfer server is missing its identity')
        accesses = ctx.call('transfer', 'list_accesses', 'Accesses', ServerId=server_id)
        values.append((server_id, len(accesses), None))
    return maximum(values, 'TransferServer', 'transfer:ListServers+ListAccesses')


def web_app_units(ctx):
    """Measure the capacity each web app runs on, which its detail reports."""
    values = []
    for summary in ctx.call('transfer', 'list_web_apps', 'WebApps'):
        identity = summary.get('WebAppId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Transfer web app is missing its identity')
        detail = ctx.call('transfer', 'describe_web_app',
                          WebAppId=identity).get('WebApp') or {}
        units = (detail.get('WebAppUnits') or {}).get('Provisioned')
        if not isinstance(units, int):
            raise NoData('Transfer web app states no provisioned units')
        values.append((identity, units, None))
    return maximum(values, 'TransferWebApp', 'transfer:DescribeWebApp')


CHECKS = [
    ('L-7E767654', 'Web apps per account', lambda ctx: resource_count(ctx, 'list_web_apps', 'WebApps')),
    ('L-B51E8407', 'Maximum web app units per web app', web_app_units),
    ('L-858EB316', 'Profiles per account', lambda ctx: resource_count(ctx, 'list_profiles', 'Profiles')),
    ('L-8A2575E3', 'Workflows per account', lambda ctx: resource_count(ctx, 'list_workflows', 'Workflows')),
    ('L-C08739CA', 'Agreements per account',
     lambda ctx: per_server(ctx, 'list_agreements', 'Agreements')),
    ('L-6E386A05', 'Servers per account', lambda ctx: resource_count(ctx, 'list_servers', 'Servers')),
    ('L-C0FDC60E', 'Certificates per account', lambda ctx: resource_count(ctx, 'list_certificates', 'Certificates')),
    ('L-A6509B77', 'Connectors per account', lambda ctx: resource_count(ctx, 'list_connectors', 'Connectors')),
    ('L-547461C3', 'AS2 connectors per account', lambda ctx: connectors_by_type(ctx, 'AS2')),
    ('L-D0C40802', 'SFTP connectors per account', lambda ctx: connectors_by_type(ctx, 'SFTP')),
    ('L-5BAD02C2', 'VPC_ENDPOINT servers per account', vpc_endpoint_servers),
    ('L-101C3D29', 'Number of Service Managed users per server', users_per_server),
    ('L-2F6B27A1', 'Logical directory mappings entries per user', logical_directory_mappings_per_user),
    ('L-B2750988', 'Certificates per profile', certificates_per_profile),
    ('L-90797EDA', 'SSH keys per Service Managed user', ssh_keys_per_service_managed_user),
    ('L-843894CE', 'Maximum number of AD Groups for access', directory_accesses_per_server),
]


def get_current_quotastatus_transfer(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'transfer' for service, _ in context.quotas):
        return []
    return context.run('transfer', CHECKS, skip)
