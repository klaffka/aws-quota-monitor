from pathlib import Path

import pytest

from modules.qmchecks.route53profiles import resources_per_profile
from modules.qmchecks.route53resolver import (
    CHECKS,
    firewall_domain_lists,
    firewall_domains,
    firewall_groups_per_vpc,
    firewall_rules_per_group,
)
from modules.qmcore.aws import NoData


class ResolverContext:
    def __init__(self):
        self.groups = [{'Id': 'group-a'}, {'Id': 'group-b'}]
        self.associations = [
            self.association('association-a', 'group-a', 'vpc-a'),
            self.association('association-b', 'group-b', 'vpc-a', 'UPDATING'),
            self.association('association-c', 'group-a', 'vpc-b', 'DELETING'),
        ]
        self.rules = {
            'group-a': [self.rule('group-a', priority) for priority in (100, 200, 300)],
            'group-b': [self.rule('group-b', 100)],
        }
        self.profiles = [
            {'Id': 'profile-a', 'Arn': 'arn:profile:a', 'ShareStatus': 'NOT_SHARED'},
            {'Id': 'profile-b', 'Arn': 'arn:profile:b', 'ShareStatus': 'SHARED_BY_ME'},
        ]
        self.profile_resources = {
            'profile-a': [
                self.resource('resource-a', 'profile-a', 'RESOLVER_RULE'),
                self.resource('resource-b', 'profile-a', 'RESOLVER_RULE'),
                self.resource('resource-c', 'profile-a', 'FIREWALL_RULE_GROUP'),
            ],
            'profile-b': [
                self.resource('resource-d', 'profile-b', 'RESOLVER_RULE'),
                self.resource('resource-e', 'profile-b', 'FIREWALL_RULE_GROUP'),
                self.resource('resource-f', 'profile-b', 'FIREWALL_RULE_GROUP'),
            ],
        }

    @staticmethod
    def association(identity, group, vpc, status='COMPLETE'):
        return {'Id': identity, 'FirewallRuleGroupId': group,
                'VpcId': vpc, 'Status': status}

    @staticmethod
    def rule(group, priority):
        return {'FirewallRuleGroupId': group, 'Priority': priority}

    @staticmethod
    def resource(identity, profile, resource_type):
        return {'Id': identity, 'ProfileId': profile,
                'ResourceArn': f'arn:resource:{identity}',
                'ResourceType': resource_type, 'Status': 'COMPLETE'}

    def call(self, service, method, key=None, **kwargs):
        if service == 'route53resolver':
            if method == 'list_firewall_rule_group_associations':
                return self.associations
            if method == 'list_firewall_rule_groups':
                return self.groups
            if method == 'list_firewall_rules':
                return self.rules[kwargs['FirewallRuleGroupId']]
        if service == 'route53profiles':
            if method == 'list_profiles':
                return self.profiles
            if method == 'list_profile_resource_associations':
                return self.profile_resources[kwargs['ProfileId']]
        raise AssertionError((service, method, key, kwargs))


def test_firewall_group_associations_use_maximum_per_vpc():
    result = firewall_groups_per_vpc(ResolverContext())
    assert (result['usage'], result['resource_id']) == (2, 'vpc-a')
    assert result['meta'] is None


def test_firewall_rules_use_maximum_per_group():
    result = firewall_rules_per_group(ResolverContext())
    assert (result['usage'], result['resource_id']) == (3, 'group-a')
    assert result['meta'] is None


def test_resolver_profile_resources_use_distinct_resource_types():
    ctx = ResolverContext()
    resolver_rules = resources_per_profile(ctx, 'RESOLVER_RULE')
    firewall_groups = resources_per_profile(ctx, 'FIREWALL_RULE_GROUP')
    assert (resolver_rules['usage'], resolver_rules['resource_id']) == (2, 'profile-a')
    assert (firewall_groups['usage'], firewall_groups['resource_id']) == (2, 'profile-b')


def test_resolver_domain_inventory_excludes_aws_managed_lists():
    class DomainContext:
        def call(self, service, method, key=None, **kwargs):
            assert service == 'route53resolver'
            if method == 'list_firewall_domain_lists':
                return [
                    {'Id': 'customer-list'},
                    {'Id': 'managed-list', 'ManagedOwnerName': 'Route 53 Resolver DNS Firewall'},
                ]
            assert method == 'list_firewall_domains'
            assert kwargs == {'FirewallDomainListId': 'customer-list'}
            return ['one.example', 'two.example']

    ctx = DomainContext()
    assert [item['Id'] for item in firewall_domain_lists(ctx)] == ['customer-list']
    assert firewall_domains(ctx) == ['one.example', 'two.example']


def test_resolver_firewall_inventories_reject_duplicates_and_parent_mismatches():
    ctx = ResolverContext()
    ctx.associations.append(dict(ctx.associations[0]))
    with pytest.raises(NoData, match='has a duplicate'):
        firewall_groups_per_vpc(ctx)

    ctx = ResolverContext()
    ctx.rules['group-a'][0]['FirewallRuleGroupId'] = 'group-b'
    with pytest.raises(NoData, match='is inconsistent'):
        firewall_rules_per_group(ctx)


def test_route53resolver_registers_all_measurable_catalog_quotas():
    codes = {code for code, _, _ in CHECKS}
    assert len(codes) == len(CHECKS) == 12
    assert {'L-15219E1D', 'L-8B4B9B75', 'L-F763F4D9', 'L-F8A07EF1'} <= codes
    assert 'L-1B2BDF0A' not in codes


def test_route53resolver_configuration_has_read_permissions():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"route53resolver:ListFirewallRuleGroupAssociations"' in policy
    assert '"route53resolver:ListFirewallRules"' in policy
    assert '"route53profiles:ListProfileResourceAssociations"' in policy
