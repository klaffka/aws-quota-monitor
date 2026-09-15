"""AWS AppSync GraphQL and Event API inventories.

The size, payload, execution time and iteration quotas bound a single request or
document rather than an inventory, and subscriptions per client connection count
live connections that no API lists.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

APPSYNC = 'appsync'


def graphql_apis(ctx):
    found = {}
    for api in ctx.call(APPSYNC, 'list_graphql_apis', 'graphqlApis'):
        identity = api.get('apiId')
        if not isinstance(identity, str) or not identity:
            raise NoData('AppSync API is missing its identity')
        found[identity] = api
    return found


def event_apis(ctx):
    found = {}
    for api in ctx.call(APPSYNC, 'list_apis', 'apis'):
        identity = api.get('apiId')
        if not isinstance(identity, str) or not identity:
            raise NoData('AppSync Event API is missing its identity')
        found[identity] = api
    return found


def _per_api(inventory, method, key, source, **kwargs):
    def check(ctx):
        values = [(identity, len(ctx.call(APPSYNC, method, key, apiId=identity, **kwargs)),
                   None)
                  for identity in inventory(ctx)]
        return maximum(values, 'AppSyncApi', source)
    return check


def authentication_providers_per_api(ctx):
    """The primary authentication type counts alongside the additional ones."""
    values = []
    for identity, api in graphql_apis(ctx).items():
        if not api.get('authenticationType'):
            raise NoData('AppSync API has no authentication type')
        additional = api.get('additionalAuthenticationProviders') or []
        if not isinstance(additional, list):
            raise NoData('AppSync API has an invalid authentication provider list')
        values.append((identity, 1 + len(additional), None))
    return maximum(values, 'AppSyncApi', 'appsync:ListGraphqlApis')


def functions_per_pipeline_resolver(ctx):
    values = []
    for identity in graphql_apis(ctx):
        for schema_type in ctx.call(APPSYNC, 'list_types', 'types', apiId=identity,
                                    format='SDL'):
            name = schema_type.get('name')
            if not isinstance(name, str) or not name:
                raise NoData('AppSync type is missing its name')
            for resolver in ctx.call(APPSYNC, 'list_resolvers', 'resolvers',
                                     apiId=identity, typeName=name):
                pipeline = resolver.get('pipelineConfig') or {}
                functions = pipeline.get('functions') or []
                if not isinstance(functions, list):
                    raise NoData('AppSync resolver has an invalid pipeline')
                values.append((f"{identity}/{name}/{resolver.get('fieldName')}",
                               len(functions), None))
    return maximum(values, 'AppSyncResolver', 'appsync:ListResolvers')


CHECKS = [
    ('L-4DFA3D2F', 'GraphQL APIs per region',
     lambda ctx: dict(usage=len(graphql_apis(ctx)), source='appsync:ListGraphqlApis',
                      method='ACCOUNT_COUNT')),
    ('L-D19E6EC4', 'Event APIs - APIs per region',
     lambda ctx: dict(usage=len(event_apis(ctx)), source='appsync:ListApis',
                      method='ACCOUNT_COUNT')),
    ('L-06A0647C', 'All APIs - API keys per API',
     _per_api(graphql_apis, 'list_api_keys', 'apiKeys', 'appsync:ListApiKeys')),
    ('L-E7CCBB11', 'All APIs - Authentication providers per API',
     authentication_providers_per_api),
    ('L-855DA767', 'All APIs - Functions per pipeline resolver or handler',
     functions_per_pipeline_resolver),
    ('L-39784425', 'Event APIs - Channel namespaces per API',
     _per_api(event_apis, 'list_channel_namespaces', 'channelNamespaces',
              'appsync:ListChannelNamespaces')),
    ('L-3B7F188C', 'GraphQL APIs - Source API associations per Merged API',
     _per_api(graphql_apis, 'list_source_api_associations',
              'sourceApiAssociationSummaries', 'appsync:ListSourceApiAssociations')),
]


def get_current_quotastatus_appsync(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appsync' for service, _ in context.quotas):
        return []
    return context.run('appsync', CHECKS, skip)
