"""AgentCore account and parent-scoped quotas from complete API inventories."""
from datetime import datetime, timedelta
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CONTROL = 'bedrock-agentcore-control'
SERVICE = 'bedrock-agentcore'


def inventory(ctx, method, key, **kwargs):
    return [item for item in ctx.call(CONTROL, method, key, **kwargs)
            if item.get('status') != 'DELETED']


def account_count(ctx, method, key, **kwargs):
    return dict(usage=len(inventory(ctx, method, key, **kwargs)),
                source=f'{CONTROL}:{method}', method='ACCOUNT_COUNT')


def parent_count(ctx, parent_method, parent_key, identifier, child_method, child_key, parameter):
    values = []
    for parent in inventory(ctx, parent_method, parent_key):
        parent_id = parent[identifier]
        children = inventory(ctx, child_method, child_key, **{parameter: parent_id})
        values.append((parent_id, len(children), None))
    return maximum(values, identifier, f'{CONTROL}:{parent_method}+{child_method}')


def memory_strategies(ctx, strategy_type=None, total=False):
    values = []
    for memory in inventory(ctx, 'list_memories', 'memories'):
        details = ctx.call(CONTROL, 'get_memory', memoryId=memory['id'], view='without_decryption')['memory']
        strategies = details.get('strategies', [])
        if strategy_type and any(not s.get('type') for s in strategies):
            raise NoData('AgentCore memory strategy has no type')
        count = sum(strategy_type is None or s['type'] == strategy_type for s in strategies)
        values.append((memory['id'], count, None))
    source = f'{CONTROL}:ListMemories+GetMemory'
    if total:
        return dict(usage=sum(v[1] for v in values), source=source, method='ACCOUNT_COUNT')
    return maximum(values, 'AgentCoreMemory', source)


def active_sessions(ctx, browser):
    list_method, list_key, identifier, session_method, parameter = (
        ('list_browsers', 'browserSummaries', 'browserId', 'list_browser_sessions', 'browserIdentifier')
        if browser else ('list_code_interpreters', 'codeInterpreterSummaries', 'codeInterpreterId',
                         'list_code_interpreter_sessions', 'codeInterpreterIdentifier'))
    sessions = set()
    tools = {}
    # The built-in aws.browser.v1/aws.codeinterpreter.v1 tools consume session
    # quotas too, although only CUSTOM tools consume configuration quotas.
    for tool_type in ('CUSTOM', 'SYSTEM'):
        for tool in inventory(ctx, list_method, list_key, type=tool_type):
            tools[tool[identifier]] = tool
    for tool_id in tools:
        for session in ctx.call(SERVICE, session_method, 'items', **{parameter: tool_id}, status='READY'):
            if session.get('status') != 'READY':
                raise NoData('AgentCore returned a session outside the requested READY status')
            sessions.add((tool_id, session['sessionId']))
    return dict(usage=len(sessions), source=f'{SERVICE}:{session_method}', method='ACCOUNT_COUNT')


def generated_policies(ctx, days=7):
    """Count the policy generations inside the quota's rolling window."""
    window = ctx.now - timedelta(days=days)
    values = []
    for engine in inventory(ctx, 'list_policy_engines', 'policyEngines'):
        identity = engine['policyEngineId']
        usage = 0
        for generation in ctx.call(CONTROL, 'list_policy_generations',
                                   'policyGenerations', policyEngineId=identity):
            created = generation.get('createdAt')
            if not isinstance(created, datetime):
                raise NoData('AgentCore policy generation has no creation time')
            usage += created >= window
        values.append((identity, usage, None))
    return maximum(values, 'AgentCorePolicyEngine',
                   f'{CONTROL}:ListPolicyGenerations')


def rate_limit_configuration(ctx, field):
    values = []
    for gateway in inventory(ctx, 'list_gateways', 'items'):
        gateway_id = gateway['gatewayId']
        for limit in inventory(ctx, 'list_gateway_rate_limits', 'rateLimits', gatewayIdentifier=gateway_id):
            # The list API returns full rate-limit details, including both
            # dimensionKeys and entries; no per-limit requests are necessary.
            entries = limit.get(field)
            if not isinstance(entries, list):
                raise NoData(f'AgentCore rate limit is missing {field}')
            values.append((f"{gateway_id}/{limit['rateLimitId']}", len(entries), None))
    return maximum(values, 'AgentCoreGatewayRateLimit', f'{CONTROL}:ListGatewayRateLimits')


ACCOUNT_CHECKS = (
    ('L-F4575653', 'Total Agents per Account', 'list_agent_runtimes', 'agentRuntimes', {}),
    ('L-81002DCC', 'Memories', 'list_memories', 'memories', {}),
    ('L-410A4D7F', 'Gateways per Region', 'list_gateways', 'items', {}),
    ('L-2E13D7FD', 'Workload identities', 'list_workload_identities', 'workloadIdentities', {}),
    ('L-B04D9A86', 'Resource API key credential providers', 'list_api_key_credential_providers', 'credentialProviders', {}),
    ('L-431051DC', 'Resource OAuth2 credential providers', 'list_oauth2_credential_providers', 'credentialProviders', {}),
    ('L-BC1EB745', 'Resource Payment credential providers', 'list_payment_credential_providers', 'credentialProviders', {}),
    ('L-D8BDCBA9', 'Total Code Interpreter tool configurations per account', 'list_code_interpreters', 'codeInterpreterSummaries', {'type': 'CUSTOM'}),
    ('L-24EE20EE', 'Total Browser tool configurations per Account', 'list_browsers', 'browserSummaries', {'type': 'CUSTOM'}),
    ('L-14434856', 'Total Browser profiles per Account', 'list_browser_profiles', 'profileSummaries', {}),
    ('L-538FCB7D', 'Policy Engines per Region', 'list_policy_engines', 'policyEngines', {}),
    ('L-16344246', 'PaymentManagers per account', 'list_payment_managers', 'paymentManagers', {}),
)

PARENT_CHECKS = (
    ('L-9B442722', 'Endpoints per Agent', 'list_agent_runtimes', 'agentRuntimes', 'agentRuntimeId', 'list_agent_runtime_endpoints', 'runtimeEndpoints', 'agentRuntimeId'),
    ('L-61A3A6D8', 'Versions per Agent', 'list_agent_runtimes', 'agentRuntimes', 'agentRuntimeId', 'list_agent_runtime_versions', 'agentRuntimes', 'agentRuntimeId'),
    ('L-3601D726', 'Targets per gateway', 'list_gateways', 'items', 'gatewayId', 'list_gateway_targets', 'items', 'gatewayIdentifier'),
    ('L-83AABACC', 'Rate limits per gateway', 'list_gateways', 'items', 'gatewayId', 'list_gateway_rate_limits', 'rateLimits', 'gatewayIdentifier'),
    ('L-A5B5E41D', 'Policies per Policy Engine', 'list_policy_engines', 'policyEngines', 'policyEngineId', 'list_policies', 'policies', 'policyEngineId'),
    ('L-0AAC669F', 'PaymentConnectors per PaymentManager', 'list_payment_managers', 'paymentManagers', 'paymentManagerId', 'list_payment_connectors', 'paymentConnectors', 'paymentManagerId'),
)

CHECKS = [(code, name, partial(account_count, method=method, key=key, **kwargs))
          for code, name, method, key, kwargs in ACCOUNT_CHECKS]
CHECKS += [(code, name, partial(parent_count, parent_method=pm, parent_key=pk, identifier=identifier,
                              child_method=cm, child_key=ck, parameter=parameter))
           for code, name, pm, pk, identifier, cm, ck, parameter in PARENT_CHECKS]
CHECKS += [
    ('L-EAB901C0', 'Memory strategies per memory', memory_strategies),
    ('L-F83DDFE4', 'Memory strategies per account', partial(memory_strategies, total=True)),
    ('L-70CA6545', 'Built-in user preferences strategy types per memory', partial(memory_strategies, strategy_type='USER_PREFERENCE')),
    ('L-01F2EA4D', 'Built-in summary strategy types per memory', partial(memory_strategies, strategy_type='SUMMARIZATION')),
    ('L-694AAA61', 'Built-in semantic strategy types per memory', partial(memory_strategies, strategy_type='SEMANTIC')),
    ('L-1CB82154', 'Total concurrent active browser sessions per account', partial(active_sessions, browser=True)),
    ('L-CAF6F552', 'Total concurrent active code interpreter sessions per account', partial(active_sessions, browser=False)),
    ('L-59D3ABC4', 'Entries per rate limit', partial(rate_limit_configuration, field='entries')),
    ('L-F262C8D7', 'Dimension keys per rate limit', partial(rate_limit_configuration, field='dimensionKeys')),
    ('L-8DE3076E', 'Generated Policies (7 day rolling window) per Policy Engine',
     generated_policies),
]


def get_current_quotastatus_bedrock_agentcore(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    checks = [check for check in CHECKS if (SERVICE, check[0]) in context.quotas]
    return context.run(SERVICE, checks, skip)
