"""AWS IoT Core endpoint, rule, thing group, policy and logging inventories.

The MQTT protocol quotas describe one connection or message: unacknowledged
publishes, topic aliases, subscriptions per connection, shared subscription
groups and expiry intervals all live in the broker rather than in an inventory.

`Maximum number of retained messages per account` is not measured here although
the data plane would answer it: AWS publishes an official usage metric for it
(`AWS/Usage` `ResourceCount`, resource `ApproximateRetainedMessageCount`), and
an official metric wins over a resource check, so the check would never run.

The thing-scoped quotas -- attributes on a thing with and without a thing type,
thing groups a thing belongs to, thing types associated with a thing -- would
each need a describe for every thing in the registry, which a fleet makes
unbounded. `Maximum number of CA certificates with the same subject field` is
blocked for a different reason: DescribeCACertificate reports the certificate as
PEM and never as a parsed subject, and reading a subject out of it would need an
X.509 parser this package does not ship.
"""
from collections import Counter

from modules.qmchecks.iot import dynamic_thing_groups
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

IOT = 'iot'


def _count(method, key, source):
    return lambda ctx: dict(usage=len(ctx.call(IOT, method, key)), source=source,
                            method='ACCOUNT_COUNT')


def topic_rule_actions(ctx):
    """Yield (rule name, its actions) for every topic rule, detail included."""
    for summary in ctx.call(IOT, 'list_topic_rules', 'rules'):
        name = summary.get('ruleName')
        if not isinstance(name, str) or not name:
            raise NoData('IoT topic rule is missing its name')
        rule = ctx.call(IOT, 'get_topic_rule', ruleName=name).get('rule')
        if not isinstance(rule, dict):
            raise NoData('IoT topic rule has no detail')
        actions = rule.get('actions') or []
        if not isinstance(actions, list):
            raise NoData('IoT topic rule has an invalid action list')
        yield name, actions


def actions_per_topic_rule(ctx):
    values = [(name, len(actions), None)
              for name, actions in topic_rule_actions(ctx)]
    return maximum(values, 'IoTTopicRule', 'iot:GetTopicRule')


def headers_per_http_action(ctx):
    """An action is one kind of sink; only the HTTP one carries headers."""
    values = []
    for name, actions in topic_rule_actions(ctx):
        for index, action in enumerate(actions):
            http = action.get('http')
            if not isinstance(http, dict):
                continue
            headers = http.get('headers') or []
            if not isinstance(headers, list):
                raise NoData('IoT HTTP action has an invalid header list')
            values.append((f'{name}#{index}', len(headers), None))
    return maximum(values, 'IoTTopicRuleAction', 'iot:GetTopicRule')


def policies_per_target(ctx):
    """Count the policies on a target rather than the targets on a policy.

    The quota bounds what may be attached to one certificate or Cognito
    identity. Walking certificates would reach only half of that, because a
    Cognito identity has no listing; every target of either kind is named by
    the policy it is attached to, so the walk is made from the policy side.
    """
    counts = Counter()
    for policy in ctx.call(IOT, 'list_policies', 'policies'):
        name = policy.get('policyName') or policy.get('name')
        if not isinstance(name, str) or not name:
            raise NoData('IoT policy is missing its name')
        for target in ctx.call(IOT, 'list_targets_for_policy', 'targets',
                               policyName=name):
            if not isinstance(target, str) or not target:
                raise NoData('IoT policy names an invalid target')
            counts[target] += 1
    return maximum(((target, count, None) for target, count in counts.items()),
                   'IoTPolicyTarget', 'iot:ListTargetsForPolicy')


def propagating_attributes(ctx):
    """A thing type propagates MQTT 5 user properties; one setting none has zero."""
    values = []
    for thing_type in ctx.call(IOT, 'list_thing_types', 'thingTypes'):
        name = thing_type.get('thingTypeName')
        if not isinstance(name, str) or not name:
            raise NoData('IoT thing type is missing its name')
        properties = thing_type.get('thingTypeProperties') or {}
        mqtt5 = properties.get('mqtt5Configuration') or {}
        attributes = mqtt5.get('propagatingAttributes') or []
        if not isinstance(attributes, list):
            raise NoData('IoT thing type has an invalid propagating attribute list')
        values.append((name, len(attributes), None))
    return maximum(values, 'IoTThingType', 'iot:ListThingTypes')


def thing_groups(ctx):
    found = []
    for group in ctx.call(IOT, 'list_thing_groups', 'thingGroups'):
        name = group.get('groupName')
        if not isinstance(name, str) or not name:
            raise NoData('IoT thing group is missing its name')
        found.append(name)
    return found


def _thing_group_detail(name, ctx):
    detail = ctx.call(IOT, 'describe_thing_group', thingGroupName=name)
    if not isinstance(detail, dict) or not detail.get('thingGroupName'):
        raise NoData('IoT thing group has no detail')
    return detail


def attributes_per_thing_group(ctx):
    values = []
    for name in thing_groups(ctx):
        properties = _thing_group_detail(name, ctx).get('thingGroupProperties') or {}
        payload = properties.get('attributePayload') or {}
        attributes = payload.get('attributes') or {}
        if not isinstance(attributes, dict):
            raise NoData('IoT thing group has an invalid attribute map')
        values.append((name, len(attributes), None))
    return maximum(values, 'IoTThingGroup', 'iot:DescribeThingGroup')


def thing_group_hierarchy_depth(ctx):
    """A group's ancestors are listed on it, so the depth needs no walk."""
    values = []
    for name in thing_groups(ctx):
        metadata = _thing_group_detail(name, ctx).get('thingGroupMetadata') or {}
        ancestors = metadata.get('rootToParentThingGroups') or []
        if not isinstance(ancestors, list):
            raise NoData('IoT thing group has an invalid ancestor list')
        values.append((name, len(ancestors) + 1, None))
    return maximum(values, 'IoTThingGroup', 'iot:DescribeThingGroup')


def direct_child_groups(ctx):
    values = []
    for name in thing_groups(ctx):
        children = ctx.call(IOT, 'list_thing_groups', 'thingGroups',
                            parentGroup=name, recursive=False)
        values.append((name, len(children), None))
    return maximum(values, 'IoTThingGroup', 'iot:ListThingGroups')


def provisioning_template_versions(ctx):
    """Return the largest version inventory for any fleet template.

    The quota is scoped to one template, so an account-wide sum would be
    misleading.  ListProvisioningTemplateVersions is parent-scoped and the
    shared context handles pagination and failed inventories atomically.
    """
    values = []
    for template in ctx.call('iot', 'list_provisioning_templates', 'templates'):
        name = template.get('templateName') or template.get('name')
        if name:
            versions = ctx.call('iot', 'list_provisioning_template_versions', 'versions',
                                templateName=name)
            values.append((name, len(versions), None))
    return maximum(values, 'FleetProvisioningTemplate',
                   'iot:ListProvisioningTemplates+ListProvisioningTemplateVersions')


def policy_versions(ctx):
    """Return the largest named-policy version inventory.

    IoT limits named policy versions per policy.  Taking the maximum across
    policies preserves that parent scope and avoids inventing an account-wide
    quota by summing unrelated policies.
    """
    values = []
    for policy in ctx.call('iot', 'list_policies', 'policies'):
        name = policy.get('policyName') or policy.get('name')
        if name:
            versions = ctx.call('iot', 'list_policy_versions', 'policyVersions',
                                policyName=name)
            values.append((name, len(versions), None))
    return maximum(values, 'IoTNamedPolicy', 'iot:ListPolicies+ListPolicyVersions')


CHECKS = [
    ('L-345B62A1', 'Maximum number of fleet provisioning templates per customer',
     lambda c: dict(usage=len(c.call('iot', 'list_provisioning_templates', 'templates')),
                    source='iot:ListProvisioningTemplates', method='ACCOUNT_COUNT')),
    ('L-8AF17D80', 'Maximum number of AWS IoT Core role aliases',
     lambda c: dict(usage=len(c.call('iot', 'list_role_aliases', 'roleAliases')),
                    source='iot:ListRoleAliases', method='ACCOUNT_COUNT')),
    ('L-78E3C43F', 'Custom authentication: maximum number of authorizers per account',
     lambda c: dict(usage=len(c.call('iot', 'list_authorizers', 'authorizers')),
                    source='iot:ListAuthorizers', method='ACCOUNT_COUNT')),
    ('L-FC25158E', 'Custom authentication: maximum number of active authorizers per account',
     lambda c: dict(usage=len([a for a in c.call('iot', 'list_authorizers', 'authorizers')
                               if a.get('status') == 'ACTIVE']),
                    source='iot:ListAuthorizers', method='ACCOUNT_COUNT')),
    ('L-954FA751', 'Maximum number of rules per AWS account',
     lambda c: dict(usage=len(c.call('iot', 'list_topic_rules', 'rules')),
                    source='iot:ListTopicRules', method='ACCOUNT_COUNT')),
    ('L-71FA7EC4', 'Maximum number of fleet provisioning template versions per template',
     provisioning_template_versions),
    ('L-5F6C2444', 'Maximum number of named policy versions', policy_versions),
    ('L-89635276',
     'Configurable endpoints: maximum number of domain configurations per account',
     _count('list_domain_configurations', 'domainConfigurations',
            'iot:ListDomainConfigurations')),
    ('L-8E2FCD9D', 'HTTP Action: Maximum topic rule destinations per AWS account',
     _count('list_topic_rule_destinations', 'destinationSummaries',
            'iot:ListTopicRuleDestinations')),
    ('L-E1FD4738',
     'Maximum number of resource-specific logging configurations per AWS account',
     _count('list_v2_logging_levels', 'logTargetConfigurations',
            'iot:ListV2LoggingLevels')),
    ('L-E0945F24', 'Allowed registration tasks',
     _count('list_thing_registration_tasks', 'taskIds',
            'iot:ListThingRegistrationTasks')),
    ('L-51309716', 'Maximum number of actions per rule', actions_per_topic_rule),
    ('L-DC6BC7AF', 'Maximum number of attributes associated with a thing group',
     attributes_per_thing_group),
    ('L-1AC7411F', 'Maximum depth of a thing group hierarchy',
     thing_group_hierarchy_depth),
    ('L-9D744041', 'Maximum number of direct child groups', direct_child_groups),
    # Both service codes name this quota over the same thing group inventory.
    ('L-6EC13FE5', 'Maximum number of dynamic groups', dynamic_thing_groups),
    ('L-5C16DE50', 'HTTP Action: Maximum number of headers per action',
     headers_per_http_action),
    ('L-BC2638B3',
     'Maximum number of policies that can be attached to a certificate or '
     'Amazon Cognito identity',
     policies_per_target),
    ('L-FBACAF74', 'Maximum number of propagating attributes',
     propagating_attributes),
]


def get_current_quotastatus_iotcore(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotcore' for service, _ in context.quotas):
        return []
    return context.run('iotcore', CHECKS, skip)
