"""Regional AWS WAFv2 resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


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
]


def get_current_quotastatus_wafv2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'wafv2' for service, _ in context.quotas):
        return []
    return context.run('wafv2', CHECKS, skip)
