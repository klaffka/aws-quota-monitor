"""AWS X-Ray regional resource-count and tag quotas.

`Indexed annotations per trace` is left open: the indexing rules say which
annotations X-Ray indexes, not how many any one trace carries, and no operation
reports that.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('xray', method, key)),
                source=f'xray:{method}', method='ACCOUNT_COUNT')


def _tags_per_resource(method, key, identity, resource_type):
    """Measure the tags on one kind of resource, which each one lists itself."""
    def check(ctx):
        values = []
        for item in ctx.call('xray', method, key):
            arn = identity(item)
            if not isinstance(arn, str) or not arn:
                raise NoData(f'X-Ray {resource_type} is missing its ARN')
            tags = ctx.call('xray', 'list_tags_for_resource', 'Tags', ResourceARN=arn)
            values.append((arn, len(tags), None))
        return maximum(values, resource_type, 'xray:ListTagsForResource')
    return check


CHECKS = [
    ('L-7F259013', 'Groups in an account',
     lambda ctx: resource_count(ctx, 'get_groups', 'Groups')),
    ('L-8C0C998A', 'Custom sampling rules per region',
     lambda ctx: resource_count(ctx, 'get_sampling_rules', 'SamplingRuleRecords')),
    ('L-E2DD2778', 'Tags per group',
     _tags_per_resource('get_groups', 'Groups',
                        lambda item: item.get('GroupARN'), 'XRayGroup')),
    # The record wraps the rule; RuleARN names the rule, ResourceARN what it matches.
    ('L-DB51D338', 'Tags per custom sampling rule',
     _tags_per_resource('get_sampling_rules', 'SamplingRuleRecords',
                        lambda item: (item.get('SamplingRule') or {}).get('RuleARN'),
                        'XRaySamplingRule')),
]


def get_current_quotastatus_xray(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'xray' for service, _ in context.quotas):
        return []
    return context.run('xray', CHECKS, skip)
