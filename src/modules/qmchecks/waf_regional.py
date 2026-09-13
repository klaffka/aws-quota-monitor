"""Legacy regional WAF parent-scoped resource counts."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def _max_children(ctx, list_method, list_key, get_method, get_arg, response_key, child_key, resource_type):
    values = []
    for parent in ctx.call('waf-regional', list_method, list_key):
        ident = parent.get('WebACLId') or parent.get('RegexPatternSetId') or parent.get('GeoMatchSetId')
        if not ident:
            continue
        response = ctx.call('waf-regional', get_method, **{get_arg: ident})
        obj = response.get(response_key, {})
        values.append((ident, len(obj.get(child_key, [])), None))
    return maximum(values, resource_type, f'waf-regional:{get_method}')


CHECKS = [
    ('L-9692AA5E', 'Rules per web ACL', lambda c: _max_children(c, 'list_web_acls', 'WebACLs', 'get_web_acl', 'WebACLId', 'WebACL', 'Rules', 'WebACL')),
    ('L-D7382DD3', 'Patterns per pattern set', lambda c: _max_children(c, 'list_regex_pattern_sets', 'RegexPatternSets', 'get_regex_pattern_set', 'RegexPatternSetId', 'RegexPatternSet', 'Patterns', 'RegexPatternSet')),
]


def get_current_quotastatus_waf_regional(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'waf-regional' for service, _ in context.quotas):
        return []
    return context.run('waf-regional', CHECKS, skip)
