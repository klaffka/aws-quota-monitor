"""Regional AWS WAFv2 resource-count and configuration-depth quotas.

Every configuration limit is read from the full web ACL or rule group, which
only `GetWebACL` and `GetRuleGroup` return; the listings carry names and ARNs
alone. Statements nest, so each check walks a rule's statement tree rather than
its top level.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

NESTED_LISTS = ('AndStatement', 'OrStatement')
NESTED_SINGLE = ('NotStatement',)
SCOPE_DOWN = ('RateBasedStatement', 'ManagedRuleGroupStatement')


def count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call('wafv2', method, key, Scope='REGIONAL', **kwargs)),
                source=f'wafv2:{method}', method='ACCOUNT_COUNT')


def associations_per_web_acl(ctx, resource_type):
    values = []
    for acl in ctx.call('wafv2', 'list_web_acls', 'WebACLs', Scope='REGIONAL'):
        arn = acl.get('ARN')
        if arn:
            resources = ctx.call('wafv2', 'list_resources_for_web_acl',
                                 ResourceType=resource_type, WebACLArn=arn).get('ResourceArns', [])
            values.append((arn, len(resources), None))
    return maximum(values, 'WebACL', 'wafv2:ListResourcesForWebACL')


def _detail(ctx, method, key, entries, resource_type):
    """Read each listed resource in full; the summaries carry no configuration."""
    found = {}
    for entry in entries:
        identity, name = entry.get('Id'), entry.get('Name')
        if not identity or not name:
            raise NoData(f'WAFv2 {resource_type} summary is missing its identity')
        detail = ctx.call('wafv2', method, Scope='REGIONAL', Id=identity,
                          Name=name).get(key) or {}
        if detail.get('Id') != identity:
            raise NoData(f'WAFv2 {resource_type} does not match the requested identity')
        found[detail.get('ARN') or identity] = detail
    return found


def web_acls(ctx):
    return _detail(ctx, 'get_web_acl', 'WebACL',
                   ctx.call('wafv2', 'list_web_acls', 'WebACLs', Scope='REGIONAL'),
                   'web ACL')


def rule_groups(ctx):
    return _detail(ctx, 'get_rule_group', 'RuleGroup',
                   ctx.call('wafv2', 'list_rule_groups', 'RuleGroups',
                            Scope='REGIONAL'),
                   'rule group')


def containers(ctx):
    """Web ACLs and rule groups share the quotas that bound rule content."""
    return {**web_acls(ctx), **rule_groups(ctx)}


def statements(statement):
    """Yield a statement and everything nested inside it."""
    if not isinstance(statement, dict):
        raise NoData('WAFv2 rule has an invalid statement')
    yield statement
    for key in NESTED_LISTS:
        for nested in (statement.get(key) or {}).get('Statements') or []:
            yield from statements(nested)
    for key in NESTED_SINGLE:
        nested = (statement.get(key) or {}).get('Statement')
        if nested is not None:
            yield from statements(nested)
    for key in SCOPE_DOWN:
        nested = (statement.get(key) or {}).get('ScopeDownStatement')
        if nested is not None:
            yield from statements(nested)


def rule_statements(container):
    for rule in container.get('Rules') or []:
        yield from statements(rule.get('Statement'))


def _capacity(loader, resource_type):
    def check(ctx):
        values = []
        for arn, container in loader(ctx).items():
            capacity = container.get('Capacity')
            if capacity is None:
                continue
            if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
                raise NoData('WAFv2 resource has an invalid capacity')
            values.append((arn, capacity, None))
        return maximum(values, resource_type, 'wafv2:GetWebACL')
    return check


def _per_container(measure, resource_type, loader=containers):
    def check(ctx):
        values = [(arn, measure(container), None)
                  for arn, container in loader(ctx).items()]
        return maximum(values, resource_type, 'wafv2:GetWebACL+GetRuleGroup')
    return check


def _bodies(container):
    bodies = container.get('CustomResponseBodies') or {}
    if not isinstance(bodies, dict):
        raise NoData('WAFv2 resource has an invalid custom response body map')
    return bodies


def _content_length(body):
    content = body.get('Content')
    if not isinstance(content, str):
        raise NoData('WAFv2 custom response body has no content')
    return len(content.encode('utf-8')) / 1024


def largest_response_body(ctx):
    values = []
    for arn, container in containers(ctx).items():
        for key, body in _bodies(container).items():
            values.append((f'{arn}#{key}', _content_length(body), None))
    return maximum(values, 'WAFv2CustomResponseBody', 'wafv2:GetWebACL+GetRuleGroup')


def _rate_based(container):
    return sum('RateBasedStatement' in statement
               for statement in rule_statements(container))


def _actions(container):
    """Yield every custom request or response handling block a rule defines."""
    for rule in container.get('Rules') or []:
        for holder in (rule.get('Action') or {}).values():
            if isinstance(holder, dict):
                yield holder
        override = (rule.get('OverrideAction') or {}).get('Count') or {}
        if isinstance(override, dict) and override:
            yield override


def _request_headers(container):
    return [header for action in _actions(container)
            for header in ((action.get('CustomRequestHandling') or {})
                           .get('InsertHeaders') or [])]


def _response_headers(container):
    return [header for action in _actions(container)
            for header in ((action.get('CustomResponse') or {})
                           .get('ResponseHeaders') or [])]


def _largest_header_block(field, inner, resource_type):
    def check(ctx):
        values = []
        for arn, container in containers(ctx).items():
            for index, action in enumerate(_actions(container)):
                headers = (action.get(field) or {}).get(inner)
                if headers is None:
                    continue
                if not isinstance(headers, list):
                    raise NoData('WAFv2 action has an invalid header list')
                values.append((f'{arn}#{index}', len(headers), None))
        return maximum(values, resource_type, 'wafv2:GetWebACL+GetRuleGroup')
    return check


def largest_text_transformation_set(ctx):
    values = []
    for arn, container in containers(ctx).items():
        for index, statement in enumerate(rule_statements(container)):
            for body in statement.values():
                transformations = (body or {}).get('TextTransformations') \
                    if isinstance(body, dict) else None
                if transformations is None:
                    continue
                if not isinstance(transformations, list):
                    raise NoData('WAFv2 statement has invalid text transformations')
                values.append((f'{arn}#{index}', len(transformations), None))
    return maximum(values, 'WAFv2Statement', 'wafv2:GetWebACL+GetRuleGroup')


def longest_search_string(ctx):
    values = []
    for arn, container in containers(ctx).items():
        for index, statement in enumerate(rule_statements(container)):
            search = (statement.get('ByteMatchStatement') or {}).get('SearchString')
            if search is None:
                continue
            if not isinstance(search, (bytes, bytearray, str)):
                raise NoData('WAFv2 byte match statement has an invalid search string')
            length = len(search.encode('utf-8') if isinstance(search, str) else search)
            values.append((f'{arn}#{index}', length, None))
    return maximum(values, 'WAFv2Statement', 'wafv2:GetWebACL+GetRuleGroup')


def longest_regex_pattern(ctx):
    values = []
    for entry in ctx.call('wafv2', 'list_regex_pattern_sets', 'RegexPatternSets',
                          Scope='REGIONAL'):
        identity, name = entry.get('Id'), entry.get('Name')
        if not identity or not name:
            raise NoData('WAFv2 regex pattern set summary is missing its identity')
        detail = ctx.call('wafv2', 'get_regex_pattern_set', Scope='REGIONAL',
                          Id=identity, Name=name).get('RegexPatternSet') or {}
        for pattern in detail.get('RegularExpressionList') or []:
            expression = pattern.get('RegexString')
            if not isinstance(expression, str):
                raise NoData('WAFv2 regex pattern has no expression')
            values.append((identity, len(expression), None))
    return maximum(values, 'RegexPatternSet', 'wafv2:GetRegexPatternSet')


CHECKS = [
    ('L-2EC3DE7B', 'Web ACLs per account', lambda ctx: count(ctx, 'list_web_acls', 'WebACLs')),
    ('L-D6DA96AE', 'IP sets per account', lambda ctx: count(ctx, 'list_ip_sets', 'IPSets')),
    ('L-BF0029B0', 'Regex pattern sets per account',
     lambda ctx: count(ctx, 'list_regex_pattern_sets', 'RegexPatternSets')),
    ('L-C5BCD850', 'Rule groups per account', lambda ctx: count(ctx, 'list_rule_groups', 'RuleGroups')),
    ('L-B24834C1', 'IP addresses per IP set', lambda ctx: maximum(
        [(s.get('Id'), len(ctx.call('wafv2', 'get_ip_set', Scope='REGIONAL',
                                    Id=s['Id'], Name=s['Name']).get('IPSet', {}).get('Addresses', [])), None)
         for s in ctx.call('wafv2', 'list_ip_sets', 'IPSets', Scope='REGIONAL')
         if s.get('Id') and s.get('Name')], 'IPSet', 'wafv2:GetIPSet')),
    ('L-291AF103', 'Patterns per regex pattern set', lambda ctx: maximum(
        [(s.get('Id'), len(ctx.call('wafv2', 'get_regex_pattern_set', Scope='REGIONAL',
                                    Id=s['Id'], Name=s['Name']).get('RegexPatternSet', {}).get('RegularExpressionList', [])), None)
         for s in ctx.call('wafv2', 'list_regex_pattern_sets', 'RegexPatternSets', Scope='REGIONAL')
         if s.get('Id') and s.get('Name')], 'RegexPatternSet', 'wafv2:GetRegexPatternSet')),
    ('L-C5E4D334', 'ALB associations per web ACL', lambda ctx: maximum(
        [(a.get('Id'), len(ctx.call('wafv2', 'list_resources_for_web_acl', ResourceType='APPLICATION_LOAD_BALANCER',
                                    WebACLArn=a['ARN']).get('ResourceArns', [])), None)
         for a in ctx.call('wafv2', 'list_web_acls', 'WebACLs', Scope='REGIONAL')
         if a.get('ARN')], 'WebACL', 'wafv2:ListResourcesForWebACL')),
    ('L-B32E8672', 'API Gateway REST API associations per web ACL', lambda c: associations_per_web_acl(c, 'API_GATEWAY')),
    ('L-5B2F9B11', 'AppSync GraphQL API associations per web ACL', lambda c: associations_per_web_acl(c, 'APPSYNC')),
    ('L-9FD4FE94', 'Cognito user pool associations per web ACL', lambda c: associations_per_web_acl(c, 'COGNITO_USER_POOL')),
    ('L-3D6A3ADF', 'App Runner service associations per web ACL', lambda c: associations_per_web_acl(c, 'APP_RUNNER_SERVICE')),
    ('L-08788A4E', 'Verified Access instance associations per web ACL', lambda c: associations_per_web_acl(c, 'VERIFIED_ACCESS_INSTANCE')),
    ('L-D9F31E8A',
     'Maximum number of web ACL capacity units in a web ACL in WAF for regional',
     _capacity(web_acls, 'WebACL')),
    ('L-91DEFBB6',
     'Maximum number of web ACL capacity units in a rule group in WAF for regional',
     _capacity(rule_groups, 'RuleGroup')),
    ('L-11D00F38', 'Number of token domains per web ACL for regional',
     _per_container(lambda acl: len(acl.get('TokenDomains') or []), 'WebACL',
                    web_acls)),
    ('L-B1635397',
     'Maximum number of rate-based statements per web ACL in WAF for regional',
     _per_container(_rate_based, 'WebACL', web_acls)),
    ('L-9E6FF091',
     'Maximum number of rate-based statements per rule group in WAF for regional',
     _per_container(_rate_based, 'RuleGroup', rule_groups)),
    ('L-71C2E81B',
     'Maximum number of custom response bodies per web ACL or rule group for regional',
     _per_container(lambda container: len(_bodies(container)), 'WAFv2Resource')),
    ('L-6F32B880',
     ('Maximum combined size in kilobytes of all response body content for a single '
     'rule group or a single web ACL for regional'),
     _per_container(lambda container: sum(_content_length(body) for body
                                          in _bodies(container).values()),
                    'WAFv2Resource')),
    ('L-0A8A309C',
     ('Maximum size in kilobytes of the custom response body content for a single '
     'custom response definition for regional'), largest_response_body),
    ('L-2D9CB303',
     'Maximum number of custom request headers per web ACL or rule group for regional',
     _per_container(lambda container: len(_request_headers(container)),
                    'WAFv2Resource')),
    ('L-E4E414A8',
     'Maximum number of custom response headers per web ACL or rule group for regional',
     _per_container(lambda container: len(_response_headers(container)),
                    'WAFv2Resource')),
    ('L-CCCD1D7B',
     'Maximum number of custom headers for a single custom request definition for regional',
     _largest_header_block('CustomRequestHandling', 'InsertHeaders',
                           'WAFv2CustomRequestHandling')),
    ('L-45C90A8A',
     'Maximum number of custom headers for a single custom response definition for regional',
     _largest_header_block('CustomResponse', 'ResponseHeaders',
                           'WAFv2CustomResponse')),
    ('L-041DD6D3',
     'Maximum number of text transformations per rule statement for regional',
     largest_text_transformation_set),
    ('L-5E8DF1EF',
     'Maximum number of bytes in a string match (byte match) string in WAF for regional',
     longest_search_string),
    ('L-0224FEE0',
     'Maximum number of characters allowed in a regex pattern per account in WAF for regional',
     longest_regex_pattern),
]


def get_current_quotastatus_wafv2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'wafv2' for service, _ in context.quotas):
        return []
    return context.run('wafv2', CHECKS, skip)
