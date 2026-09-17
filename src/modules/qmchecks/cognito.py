"""Amazon Cognito regional user-pool inventory and per-pool scopes."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SERVICE = 'cognito-idp'
# ListUserPools requires a page size; 60 is the documented maximum.
PAGE_SIZE = 60
# ListResourceServers requires one too, and 50 is its maximum.
RESOURCE_SERVER_PAGE = 50


def user_pools(ctx):
    for pool in ctx.call(SERVICE, 'list_user_pools', 'UserPools', MaxResults=PAGE_SIZE):
        identity = pool.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Cognito user pool is missing its identity')
        yield identity


def per_user_pool(ctx, method, key, **kwargs):
    return maximum([(identity, len(ctx.call(SERVICE, method, key, UserPoolId=identity,
                                            **kwargs)), None)
                    for identity in user_pools(ctx)],
                   'CognitoUserPool', f'cognito-idp:{method}')


def scopes_per_resource_server(ctx):
    """The quota bounds one resource server's scopes, not a pool's servers."""
    values = []
    for identity in user_pools(ctx):
        for server in ctx.call(SERVICE, 'list_resource_servers', 'ResourceServers',
                               UserPoolId=identity, MaxResults=RESOURCE_SERVER_PAGE):
            name = server.get('Identifier')
            if not isinstance(name, str) or not name:
                raise NoData('Cognito resource server is missing its identifier')
            values.append((f'{identity}/{name}', len(server.get('Scopes') or ()), None))
    return maximum(values, 'CognitoResourceServer', 'cognito-idp:ListResourceServers')


CHECKS = [
    ('L-66E6DF30', 'User pools per account',
     lambda ctx: dict(usage=len(ctx.call(SERVICE, 'list_user_pools', 'UserPools', MaxResults=PAGE_SIZE)),
                      source='cognito-idp:ListUserPools', method='ACCOUNT_COUNT')),
    ('L-71267F98', 'Custom domains per account',
     lambda ctx: dict(usage=sum(bool(ctx.call(SERVICE, 'describe_user_pool', UserPoolId=identity)['UserPool'].get('CustomDomain'))
                                for identity in user_pools(ctx)),
                      source='cognito-idp:ListUserPools+DescribeUserPool', method='ACCOUNT_COUNT')),
    ('L-5EAB0605', 'Apps per user pool',
     lambda ctx: per_user_pool(ctx, 'list_user_pool_clients', 'UserPoolClients')),
    ('L-A585C375', 'Groups per user pool',
     lambda ctx: per_user_pool(ctx, 'list_groups', 'Groups')),
    ('L-1B44D826', 'Identity providers per user pool',
     lambda ctx: per_user_pool(ctx, 'list_identity_providers', 'Providers')),
    ('L-7CDAF993', 'Resource servers per user pool',
     lambda ctx: per_user_pool(ctx, 'list_resource_servers', 'ResourceServers',
                               MaxResults=RESOURCE_SERVER_PAGE)),
    ('L-770A44F8', 'Scopes per resource server', scopes_per_resource_server),
]


def get_current_quotastatus_cognito(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cognito-idp' for service, _ in context.quotas):
        return []
    return context.run('cognito-idp', CHECKS, skip)
