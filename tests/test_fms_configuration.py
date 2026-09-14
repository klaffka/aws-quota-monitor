import json
from pathlib import Path

from modules.qmchecks.fms import (apps_lists, policy_scope, protocols_lists,
                                  managed_list_maximum, network_firewall_cidrs,
                                  network_firewall_capacity,
                                  network_acl_rules, resources_per_set, tags_per_policy,
                                  wafv2_capacity, wafv2_rule_groups)


class Context:
    def __init__(self):
        self.calls = []

    def call(self, service, method, key=None, **kwargs):
        self.calls.append((method, key, kwargs))
        responses = {
            'list_apps_lists': {'AppsLists': [
                {'ListId': 'apps', 'AppsList': [{}, {}, {}]}]},
            'list_protocols_lists': {'ProtocolsLists': [
                {'ListId': 'protocols', 'ProtocolsList': ['TCP', 'UDP']}]},
            'list_resource_sets': {'ResourceSets': [{'Id': 'set-1'}]},
            'list_resource_set_resources': {'Items': [
                {'AccountId': '123456789012', 'URI': 'arn:one'},
                {'AccountId': '123456789012', 'URI': 'arn:one'},
                {'AccountId': '123456789012', 'URI': 'arn:two'}]},
            'list_policies': {'PolicyList': [{'PolicyId': 'p-1'}]},
            'get_policy': {'Policy': {
                'PolicyId': 'p-1',
                'IncludeMap': {'ACCOUNT': ['a', 'b'], 'ORG_UNIT': ['ou-1']},
                'ExcludeMap': {'ACCOUNT': ['b', 'c'], 'ORG_UNIT': ['ou-2']},
                'ResourceTags': [{'Key': 'env', 'Value': 'prod'}],
                'SecurityServicePolicyData': {
                    'Type': 'NETWORK_FIREWALL',
                    'ManagedServiceData': json.dumps({
                        'networkFirewallStatefulRuleGroupReferences': [{}, {}],
                        'networkFirewallStatelessRuleGroupReferences': [{}],
                        'networkFirewallOrchestrationConfig': {
                            'allowedIPV4CidrList': ['10.0.0.0/28', '10.0.1.0/28']},
                    }),
                },
            }},
        }
        value = responses[method]
        return value[key] if key else value


def test_managed_lists_are_explicitly_custom():
    ctx = Context()
    assert len(apps_lists(ctx)) == 1
    assert len(protocols_lists(ctx)) == 1
    assert ('list_apps_lists', 'AppsLists', {'DefaultLists': False}) in ctx.calls
    assert ('list_protocols_lists', 'ProtocolsLists', {'DefaultLists': False}) in ctx.calls


def test_resource_sets_deduplicate_resource_identity():
    assert resources_per_set(Context())['usage'] == 2


def test_policy_scope_unions_include_and_exclude_without_double_counting():
    ctx = Context()
    assert policy_scope(ctx, 'ACCOUNT')['usage'] == 3
    assert policy_scope(ctx, 'ORG_UNIT')['usage'] == 2
    assert tags_per_policy(ctx)['usage'] == 1


def test_network_firewall_managed_data_counts_references_and_nested_cidrs():
    ctx = Context()
    assert managed_list_maximum(ctx, {'NETWORK_FIREWALL'},
                                ('networkFirewallStatefulRuleGroupReferences',))['usage'] == 2
    assert network_firewall_cidrs(ctx)['usage'] == 2


def test_network_firewall_capacity_resolves_and_sums_unique_rule_groups():
    ctx = Context()
    policy = ctx.call('fms', 'get_policy')['Policy']
    policy['SecurityServicePolicyData']['ManagedServiceData'] = json.dumps({
        'networkFirewallStatefulRuleGroupReferences': [
            {'resourceARN': 'arn:rg-one'}, {'resourceARN': 'arn:rg-one'},
            {'resourceARN': 'arn:rg-two'}],
    })

    def call(service, method, key=None, **kwargs):
        if method == 'list_policies':
            return [{'PolicyId': 'p-1'}]
        if method == 'get_policy':
            return {'Policy': policy}
        arn = kwargs['RuleGroupArn']
        return {'RuleGroupResponse': {'RuleGroupArn': arn, 'Type': 'STATEFUL',
                                      'Capacity': 10 if arn.endswith('one') else 20}}

    ctx.call = call
    assert network_firewall_capacity(
        ctx, 'networkFirewallStatefulRuleGroupReferences', 'STATEFUL')['usage'] == 30


def test_wafv2_rule_groups_distinguish_partner_managed_groups():
    ctx = Context()
    policy = ctx.call('fms', 'get_policy')['Policy']
    policy['SecurityServicePolicyData'] = {
        'Type': 'WAFV2',
        'ManagedServiceData': json.dumps({
            'preProcessRuleGroups': [
                {'managedRuleGroupIdentifier': {'vendorName': 'AWS'}},
                {'managedRuleGroupIdentifier': {'vendorName': 'PartnerCo'}},
                {'ruleGroupArn': 'arn:custom'},
            ],
            'postProcessRuleGroups': [{}],
        }),
    }
    ctx.call = lambda service, method, key=None, **kwargs: (
        [{'PolicyId': 'p-1'}] if method == 'list_policies' else {'Policy': policy})
    assert wafv2_rule_groups(ctx)['usage'] == 4
    assert wafv2_rule_groups(ctx, partner_only=True)['usage'] == 1


def test_wafv2_capacity_resolves_custom_and_managed_groups():
    ctx = Context()
    policy = ctx.call('fms', 'get_policy')['Policy']
    policy.update(ResourceType='AWS::ElasticLoadBalancingV2::LoadBalancer')
    policy['SecurityServicePolicyData'] = {
        'Type': 'WAFV2',
        'ManagedServiceData': json.dumps({
            'preProcessRuleGroups': [
                {'ruleGroupArn': 'arn:custom'},
                {'managedRuleGroupIdentifier': {'vendorName': 'AWS',
                                                'managedRuleGroupName': 'Managed'}},
            ],
            'postProcessRuleGroups': [],
        }),
    }

    def call(service, method, key=None, **kwargs):
        if method == 'list_policies':
            return [{'PolicyId': 'p-1'}]
        if method == 'get_policy':
            return {'Policy': policy}
        if method == 'get_rule_group':
            return {'RuleGroup': {'ARN': 'arn:custom', 'Capacity': 100}}
        return {'Capacity': 200}

    ctx.call = call
    assert wafv2_capacity(ctx)['usage'] == 300


def test_unrelated_policy_without_managed_data_is_skipped():
    ctx = Context()
    relevant = ctx.call('fms', 'get_policy')['Policy']
    unrelated = {
        'PolicyId': 'p-shield',
        'SecurityServicePolicyData': {'Type': 'SHIELD_ADVANCED',
                                      'ManagedServiceData': 'not-json'},
    }

    def call(service, method, key=None, **kwargs):
        if method == 'list_policies':
            return [{'PolicyId': 'p-shield'}, {'PolicyId': 'p-1'}]
        policy = unrelated if kwargs['PolicyId'] == 'p-shield' else relevant
        return {'Policy': policy}

    ctx.call = call
    assert managed_list_maximum(
        ctx, {'NETWORK_FIREWALL'},
        ('networkFirewallStatefulRuleGroupReferences',))['usage'] == 2


def test_network_acl_quota_uses_larger_direction():
    ctx = Context()
    policy = ctx.call('fms', 'get_policy')['Policy']
    policy['SecurityServicePolicyData'] = {
        'Type': 'NETWORK_ACL_COMMON',
        'PolicyOption': {'NetworkAclCommonPolicy': {'NetworkAclEntrySet': {
            'FirstEntries': [{'Egress': False}, {'Egress': False}, {'Egress': True}],
            'LastEntries': [{'Egress': True}],
        }}},
    }
    ctx.call = lambda service, method, key=None, **kwargs: (
        [{'PolicyId': 'p-1'}] if method == 'list_policies' else {'Policy': policy})
    assert network_acl_rules(ctx)['usage'] == 2


def test_fms_read_permissions_are_deployed():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('GetPolicy', 'ListAppsLists', 'ListProtocolsLists', 'ListResourceSets',
                   'ListResourceSetResources', 'ListAdminAccountsForOrganization',
                   'ListMemberAccounts'):
        assert f'"fms:{action}"' in policy
    assert '"network-firewall:DescribeRuleGroup"' in policy
    assert '"wafv2:GetRuleGroup"' in policy
    assert '"wafv2:DescribeManagedRuleGroup"' in policy
