"""Recycle Bin regional rule and configuration counts."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

RESOURCE_TYPES = ('EBS_SNAPSHOT', 'EC2_IMAGE', 'EBS_VOLUME')


def rules(ctx):
    inventory = {}
    for resource_type in RESOURCE_TYPES:
        for summary in ctx.call('rbin', 'list_rules', 'Rules',
                                ResourceType=resource_type):
            if not isinstance(summary, dict):
                raise NoData('Recycle Bin rule inventory contains an invalid item')
            identifier = summary.get('Identifier')
            if (not isinstance(identifier, str) or len(identifier) != 11
                    or not identifier.isalnum()):
                raise NoData('Recycle Bin rule is missing a valid Identifier')
            if identifier in inventory:
                raise NoData('Recycle Bin rule inventory contains a duplicate Identifier')
            inventory[identifier] = resource_type
    return inventory


def rule_count(ctx):
    return dict(usage=len(rules(ctx)), source='rbin:ListRules', method='ACCOUNT_COUNT')


def tags_per_rule(ctx):
    values = []
    for identifier, resource_type in sorted(rules(ctx).items()):
        detail = ctx.call('rbin', 'get_rule', Identifier=identifier)
        if (not isinstance(detail, dict) or detail.get('Identifier') != identifier
                or detail.get('ResourceType') != resource_type):
            raise NoData('Recycle Bin rule detail is inconsistent')
        tags = detail.get('ResourceTags', [])
        if (not isinstance(tags, list)
                or any(not isinstance(tag, dict)
                       or not isinstance(tag.get('ResourceTagKey'), str)
                       or not tag['ResourceTagKey']
                       or ('ResourceTagValue' in tag
                           and not isinstance(tag['ResourceTagValue'], str))
                       for tag in tags)):
            raise NoData('Recycle Bin rule has an invalid resource-tag inventory')
        pairs = [(tag['ResourceTagKey'], tag.get('ResourceTagValue', '')) for tag in tags]
        if len(pairs) != len(set(pairs)):
            raise NoData('Recycle Bin rule has duplicate resource-tag pairs')
        values.append((identifier, len(tags), None))
    return maximum(values, 'RecycleBinRetentionRule', 'rbin:ListRules+GetRule')


CHECKS = [
    ('L-629917A2', 'Rules per Region', rule_count),
    ('L-BCC6359E', 'Tags per rule', tags_per_rule),
]

def get_current_quotastatus_rbin(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rbin' for service, _ in context.quotas): return []
    return context.run('rbin', CHECKS, skip)
