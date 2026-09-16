"""Legacy regional WAF (WAF Classic) inventories and condition depth.

Each match condition keeps its filters in its own detail call; the listings
return names and identities alone.
"""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

WAF_REGIONAL = 'waf-regional'
# Listing, its output key, the identity field, the detail call and the list
# inside that detail which the per-resource quotas bound.
CONDITIONS = {
    'geo': ('list_geo_match_sets', 'GeoMatchSets', 'GeoMatchSetId',
            'get_geo_match_set', 'GeoMatchSet', 'GeoMatchConstraints'),
    'ip': ('list_ip_sets', 'IPSets', 'IPSetId', 'get_ip_set', 'IPSet',
           'IPSetDescriptors'),
    'size': ('list_size_constraint_sets', 'SizeConstraintSets',
             'SizeConstraintSetId', 'get_size_constraint_set',
             'SizeConstraintSet', 'SizeConstraints'),
    'sqli': ('list_sql_injection_match_sets', 'SqlInjectionMatchSets',
             'SqlInjectionMatchSetId', 'get_sql_injection_match_set',
             'SqlInjectionMatchSet', 'SqlInjectionMatchTuples'),
    'xss': ('list_xss_match_sets', 'XssMatchSets', 'XssMatchSetId',
            'get_xss_match_set', 'XssMatchSet', 'XssMatchTuples'),
    'byte': ('list_byte_match_sets', 'ByteMatchSets', 'ByteMatchSetId',
             'get_byte_match_set', 'ByteMatchSet', 'ByteMatchTuples'),
    'regex': ('list_regex_match_sets', 'RegexMatchSets', 'RegexMatchSetId',
              'get_regex_match_set', 'RegexMatchSet', 'RegexMatchTuples'),
}


def _identities(ctx, method, key, field):
    found = []
    for entry in ctx.call(WAF_REGIONAL, method, key):
        identity = entry.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'WAF Classic resource is missing its {field}')
        found.append(identity)
    return found


def _count(method, key, field, source):
    return lambda ctx: dict(usage=len(_identities(ctx, method, key, field)),
                            source=source, method='ACCOUNT_COUNT')


def _condition_children(ctx, kind):
    """Yield each condition set of one kind with the filters it holds."""
    method, key, field, detail_method, detail_key, child = CONDITIONS[kind]
    for identity in _identities(ctx, method, key, field):
        detail = ctx.call(WAF_REGIONAL, detail_method,
                          **{field: identity}).get(detail_key) or {}
        if detail.get(field) != identity:
            raise NoData('WAF Classic condition detail has a different identity')
        children = detail.get(child)
        if not isinstance(children, list):
            raise NoData(f'WAF Classic condition has no {child} list')
        yield identity, children


def _filters_per_condition(kind, resource_type):
    def check(ctx):
        values = [(identity, len(children), None)
                  for identity, children in _condition_children(ctx, kind)]
        return maximum(values, resource_type,
                       f'waf-regional:{CONDITIONS[kind][3]}')
    return check


def _max_children(ctx, list_method, list_key, get_method, get_arg, response_key,
                  child_key, resource_type):
    values = []
    for identity in _identities(ctx, list_method, list_key, get_arg):
        response = ctx.call(WAF_REGIONAL, get_method, **{get_arg: identity})
        obj = response.get(response_key) or {}
        children = obj.get(child_key)
        if not isinstance(children, list):
            raise NoData(f'WAF Classic resource has no {child_key} list')
        values.append((identity, len(children), None))
    return maximum(values, resource_type, f'waf-regional:{get_method}')


def predicates_per_rule(ctx):
    """A rule's predicates are the conditions it combines."""
    return _max_children(ctx, 'list_rules', 'Rules', 'get_rule', 'RuleId', 'Rule',
                         'Predicates', 'WAFRule')


def pattern_sets_per_regex_condition(ctx):
    values = [(identity, len(children), None)
              for identity, children in _condition_children(ctx, 'regex')]
    return maximum(values, 'RegexMatchSet', 'waf-regional:GetRegexMatchSet')


def logging_destinations_per_web_acl(ctx):
    values = []
    for configuration in ctx.call(WAF_REGIONAL, 'list_logging_configurations',
                                  'LoggingConfigurations'):
        arn = configuration.get('ResourceArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('WAF Classic logging configuration has no resource')
        destinations = configuration.get('LogDestinationConfigs')
        if not isinstance(destinations, list):
            raise NoData('WAF Classic logging configuration has no destinations')
        values.append((arn, len(destinations), None))
    return maximum(values, 'WebACL', 'waf-regional:ListLoggingConfigurations')


def locations_per_geo_match_set(ctx):
    counts = Counter()
    for identity, constraints in _condition_children(ctx, 'geo'):
        for constraint in constraints:
            if not constraint.get('Value'):
                raise NoData('WAF Classic geo match constraint has no value')
            counts[identity] += 1
    return maximum(((identity, count, None) for identity, count in counts.items()),
                   'GeoMatchSet', 'waf-regional:GetGeoMatchSet')


CHECKS = [
    ('L-9692AA5E', 'Rules per web ACL',
     lambda ctx: _max_children(ctx, 'list_web_acls', 'WebACLs', 'get_web_acl',
                               'WebACLId', 'WebACL', 'Rules', 'WebACL')),
    ('L-D7382DD3', 'Patterns per pattern set',
     lambda ctx: _max_children(ctx, 'list_regex_pattern_sets', 'RegexPatternSets',
                               'get_regex_pattern_set', 'RegexPatternSetId',
                               'RegexPatternSet', 'RegexPatternStrings',
                               'RegexPatternSet')),
    ('L-55785BA2', 'Web ACLs',
     _count('list_web_acls', 'WebACLs', 'WebACLId', 'waf-regional:ListWebACLs')),
    ('L-7BF8015E', 'Rules',
     _count('list_rules', 'Rules', 'RuleId', 'waf-regional:ListRules')),
    ('L-6DA23DDF', 'Rate-based rules',
     _count('list_rate_based_rules', 'Rules', 'RuleId',
            'waf-regional:ListRateBasedRules')),
    ('L-8EEF0989', 'Regex pattern sets',
     _count('list_regex_pattern_sets', 'RegexPatternSets', 'RegexPatternSetId',
            'waf-regional:ListRegexPatternSets')),
    ('L-ACF59499', 'GeoMatchSets',
     _count('list_geo_match_sets', 'GeoMatchSets', 'GeoMatchSetId',
            'waf-regional:ListGeoMatchSets')),
    ('L-9C634948', 'Conditions per rule', predicates_per_rule),
    ('L-FFB853E8', 'Locations per GeoMatchSet', locations_per_geo_match_set),
    ('L-AF52C91B', 'IP address ranges per IP set match condition',
     _filters_per_condition('ip', 'IPSet')),
    ('L-5510BCA0', 'Filters per size constraint condition',
     _filters_per_condition('size', 'SizeConstraintSet')),
    ('L-954F3F3A', 'Filters per SQL injection match condition',
     _filters_per_condition('sqli', 'SqlInjectionMatchSet')),
    ('L-EFDFFE2D', 'Filters per cross-site scripting match condition',
     _filters_per_condition('xss', 'XssMatchSet')),
    ('L-C47A352B', 'Filters per string match condition',
     _filters_per_condition('byte', 'ByteMatchSet')),
    ('L-DF027FCD', 'Pattern sets per regex match condition',
     pattern_sets_per_regex_condition),
    ('L-0043356F', 'Logging destination configurations per web ACL',
     logging_destinations_per_web_acl),
]


def get_current_quotastatus_waf_regional(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == WAF_REGIONAL for service, _ in context.quotas):
        return []
    return context.run(WAF_REGIONAL, CHECKS, skip)
