"""AWS AppSync regional API inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-4DFA3D2F', 'GraphQL APIs per region',
     lambda ctx: dict(usage=len(ctx.call('appsync', 'list_graphql_apis', 'graphqlApis')),
                      source='appsync:ListGraphqlApis', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_appsync(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appsync' for service, _ in context.quotas): return []
    return context.run('appsync', CHECKS, skip)
