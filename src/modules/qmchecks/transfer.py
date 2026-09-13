"""AWS Transfer Family regional account resource quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('transfer', method, key)),
                source=f'transfer:{method}', method='ACCOUNT_COUNT')


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


CHECKS = [
    ('L-7E767654', 'Web apps per account', lambda ctx: resource_count(ctx, 'list_web_apps', 'WebApps')),
    ('L-858EB316', 'Profiles per account', lambda ctx: resource_count(ctx, 'list_profiles', 'Profiles')),
    ('L-8A2575E3', 'Workflows per account', lambda ctx: resource_count(ctx, 'list_workflows', 'Workflows')),
    ('L-C08739CA', 'Agreements per account', lambda ctx: resource_count(ctx, 'list_agreements', 'Agreements')),
    ('L-6E386A05', 'Servers per account', lambda ctx: resource_count(ctx, 'list_servers', 'Servers')),
    ('L-C0FDC60E', 'Certificates per account', lambda ctx: resource_count(ctx, 'list_certificates', 'Certificates')),
    ('L-A6509B77', 'Connectors per account', lambda ctx: resource_count(ctx, 'list_connectors', 'Connectors')),
    ('L-547461C3', 'AS2 connectors per account', lambda ctx: connectors_by_type(ctx, 'AS2')),
    ('L-D0C40802', 'SFTP connectors per account', lambda ctx: connectors_by_type(ctx, 'SFTP')),
    ('L-5BAD02C2', 'VPC_ENDPOINT servers per account', vpc_endpoint_servers),
    ('L-101C3D29', 'Number of Service Managed users per server', users_per_server),
    ('L-2F6B27A1', 'Logical directory mappings entries per user', logical_directory_mappings_per_user),
]


def get_current_quotastatus_transfer(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'transfer' for service, _ in context.quotas):
        return []
    return context.run('transfer', CHECKS, skip)
