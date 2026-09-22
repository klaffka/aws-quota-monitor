from unittest.mock import Mock

import pytest

from modules.qmchecks import network_firewall
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants


class NetworkFirewallContext:
    def __init__(self):
        self.firewalls = [
            {'FirewallArn': 'firewall/a'},
            {'FirewallArn': 'firewall/b'},
            {'FirewallArn': 'firewall/c'},
        ]
        self.firewall_details = {
            item['FirewallArn']: {**item, 'FirewallPolicyArn': 'policy/a'}
            for item in self.firewalls
        }
        self.policies = [{'Arn': 'policy/a'}, {'Arn': 'policy/b'}]
        self.policy_details = {
            'policy/a': {
                'FirewallPolicy': {
                    'StatelessRuleGroupReferences': [
                        {'ResourceArn': 'stateless/a'}, {'ResourceArn': 'stateless/b'}],
                    'StatefulRuleGroupReferences': [{'ResourceArn': 'stateful/a'}],
                    'TLSInspectionConfigurationArn': 'tls/a',
                },
                'FirewallPolicyResponse': {
                    'FirewallPolicyArn': 'policy/a', 'NumberOfAssociations': 3,
                    'ConsumedStatelessRuleCapacity': 7,
                    'ConsumedStatefulRuleCapacity': 9,
                },
            },
            'policy/b': {
                'FirewallPolicy': {
                    'StatelessRuleGroupReferences': [{'ResourceArn': 'stateless/a'}],
                    'StatefulRuleGroupReferences': [
                        {'ResourceArn': 'stateful/a'}, {'ResourceArn': 'stateful/b'}],
                },
                'FirewallPolicyResponse': {
                    'FirewallPolicyArn': 'policy/b', 'NumberOfAssociations': 0,
                    'ConsumedStatelessRuleCapacity': 12,
                    'ConsumedStatefulRuleCapacity': 5,
                },
            },
        }
        self.groups = {
            'STATELESS': [{'Arn': 'stateless/a'}, {'Arn': 'stateless/b'}],
            'STATEFUL': [{'Arn': 'stateful/a'}, {'Arn': 'stateful/b'}],
        }
        self.group_details = {
            ('STATELESS', 'stateless/a'): {
                'RuleGroup': {'RulesSource': {'StatelessRulesAndCustomActions': {
                    'StatelessRules': [{}, {}], 'CustomActions': [{}],
                }}},
                'RuleGroupResponse': {'RuleGroupArn': 'stateless/a', 'Type': 'STATELESS',
                                      'Capacity': 6},
            },
            ('STATELESS', 'stateless/b'): {
                'RuleGroup': {'RulesSource': {'StatelessRulesAndCustomActions': {
                    'StatelessRules': [{}, {}, {}], 'CustomActions': [{}, {}],
                }}},
                'RuleGroupResponse': {'RuleGroupArn': 'stateless/b', 'Type': 'STATELESS',
                                      'Capacity': 11},
            },
            ('STATEFUL', 'stateful/a'): {
                'RuleGroup': {
                    'ReferenceSets': {'IPSetReferences': {'HOME': {}, 'REMOTE': {}}},
                    'RulesSource': {'RulesString': 'alert tcp äny'},
                },
                'RuleGroupResponse': {'RuleGroupArn': 'stateful/a', 'Type': 'STATEFUL',
                                      'Capacity': 10},
            },
            ('STATEFUL', 'stateful/b'): {
                'RuleGroup': {
                    'ReferenceSets': {'IPSetReferences': {'OFFICE': {}}},
                    'RulesSource': {'StatefulRules': [{}]},
                },
                'RuleGroupResponse': {'RuleGroupArn': 'stateful/b', 'Type': 'STATEFUL',
                                      'Capacity': 20},
            },
        }
        self.tls = [{'Arn': 'tls/a'}, {'Arn': 'tls/b'}]
        self.tls_details = {
            'tls/a': {
                'TLSInspectionConfiguration': {'ServerCertificateConfigurations': [{
                    'ServerCertificates': [{}, {}, {}],
                    'CertificateAuthorityArn': 'certificate/ca',
                }]},
                'TLSInspectionConfigurationResponse': {
                    'TLSInspectionConfigurationArn': 'tls/a'},
            },
            'tls/b': {
                'TLSInspectionConfiguration': {},
                'TLSInspectionConfigurationResponse': {
                    'TLSInspectionConfigurationArn': 'tls/b'},
            },
        }
        self.endpoints = [
            {'VpcEndpointAssociationArn': 'endpoint/a'},
            {'VpcEndpointAssociationArn': 'endpoint/b'},
            {'VpcEndpointAssociationArn': 'endpoint/c'},
        ]
        self.endpoint_details = {
            'endpoint/a': self._endpoint('endpoint/a', 'firewall/a', 'eu-central-1a'),
            'endpoint/b': self._endpoint('endpoint/b', 'firewall/a', 'eu-central-1a'),
            'endpoint/c': self._endpoint('endpoint/c', 'firewall/b', 'eu-central-1b'),
        }
        self.containers = [{'Arn': 'container/a'}, {'Arn': 'container/b'}]
        self.container_details = {
            'container/a': self._container('container/a', [[('one', '1'), ('two', '2')],
                                                           [('three', '3')]]),
            'container/b': self._container('container/b', [[('four', '4')]]),
        }

    @staticmethod
    def _endpoint(arn, firewall_arn, az):
        return {
            'VpcEndpointAssociation': {
                'VpcEndpointAssociationArn': arn, 'FirewallArn': firewall_arn},
            'VpcEndpointAssociationStatus': {'AssociationSyncState': {az: {}}},
        }

    @staticmethod
    def _container(arn, filter_groups):
        return {
            'ContainerAssociationArn': arn,
            'ContainerMonitoringConfigurations': [
                {'AttributeFilters': [{'Key': key, 'Value': value} for key, value in filters]}
                for filters in filter_groups
            ],
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'network-firewall'
        if method == 'list_firewalls':
            return self.firewalls
        if method == 'describe_firewall':
            return {'Firewall': self.firewall_details[kwargs['FirewallArn']]}
        if method == 'list_firewall_policies':
            return self.policies
        if method == 'describe_firewall_policy':
            return self.policy_details[kwargs['FirewallPolicyArn']]
        if method == 'list_rule_groups':
            assert kwargs['Scope'] == 'ACCOUNT'
            return self.groups[kwargs['Type']]
        if method == 'describe_rule_group':
            return self.group_details[(kwargs['Type'], kwargs['RuleGroupArn'])]
        if method == 'list_tls_inspection_configurations':
            return self.tls
        if method == 'describe_tls_inspection_configuration':
            return self.tls_details[kwargs['TLSInspectionConfigurationArn']]
        if method == 'list_vpc_endpoint_associations':
            return self.endpoints
        if method == 'describe_vpc_endpoint_association':
            return self.endpoint_details[kwargs['VpcEndpointAssociationArn']]
        if method == 'list_container_associations':
            return self.containers
        if method == 'describe_container_association':
            return self.container_details[kwargs['ContainerAssociationArn']]
        raise AssertionError(method)


def test_network_firewall_policy_configuration_and_reuse_limits():
    ctx = NetworkFirewallContext()

    assert network_firewall.policy_response_maximum(
        ctx, 'NumberOfAssociations')['usage'] == 3
    assert network_firewall.policy_response_maximum(
        ctx, 'ConsumedStatelessRuleCapacity')['usage'] == 12
    assert network_firewall.policy_response_maximum(
        ctx, 'ConsumedStatefulRuleCapacity')['usage'] == 9
    assert network_firewall.policy_list_maximum(
        ctx, 'StatelessRuleGroupReferences')['usage'] == 2
    assert network_firewall.policy_list_maximum(
        ctx, 'StatefulRuleGroupReferences')['usage'] == 2
    assert network_firewall.policies_per_rule_group(ctx)['usage'] == 2
    assert network_firewall.policies_per_tls_configuration(ctx)['usage'] == 1
    assert network_firewall.tls_per_policy(ctx)['usage'] == 1
    assert network_firewall.required_policy_per_firewall(ctx)['usage'] == 1


def test_network_firewall_rule_group_and_tls_configuration_limits():
    ctx = NetworkFirewallContext()

    assert network_firewall.rule_group_maximum(ctx, 'STATELESS', 'Capacity')['usage'] == 11
    assert network_firewall.rule_group_maximum(ctx, 'STATEFUL', 'Capacity')['usage'] == 20
    assert network_firewall.rule_group_maximum(
        ctx, 'STATEFUL', 'IPSetReferences')['usage'] == 2
    assert network_firewall.rule_group_maximum(
        ctx, 'STATELESS', 'CustomActions')['usage'] == 2
    assert network_firewall.rule_group_maximum(ctx, 'STATEFUL', 'RulesString')['usage'] == len(
        'alert tcp äny'.encode())
    assert network_firewall.tls_certificate_maximum(
        ctx, 'ServerCertificates')['usage'] == 3
    assert network_firewall.tls_certificate_maximum(
        ctx, 'CertificateAuthorityArn')['usage'] == 1


def test_network_firewall_endpoint_container_and_filter_limits():
    ctx = NetworkFirewallContext()

    assert network_firewall.vpc_endpoint_count(ctx)['usage'] == 3
    endpoints = network_firewall.vpc_endpoints_per_firewall_az(ctx)
    assert (endpoints['usage'], endpoints['resource_id']) == (
        2, 'firewall/a/eu-central-1a')
    assert network_firewall.container_count(ctx)['usage'] == 2
    assert network_firewall.resource_filter_count(ctx)['usage'] == 4


def test_network_firewall_inconsistent_details_are_no_data():
    ctx = NetworkFirewallContext()
    ctx.policy_details['policy/a']['FirewallPolicyResponse']['FirewallPolicyArn'] = 'policy/other'
    with pytest.raises(NoData, match='policy detail is inconsistent'):
        network_firewall.policy_response_maximum(ctx, 'NumberOfAssociations')

    ctx = NetworkFirewallContext()
    ctx.endpoint_details['endpoint/a']['VpcEndpointAssociationStatus'] = {}
    with pytest.raises(NoData, match='invalid scope data'):
        network_firewall.vpc_endpoints_per_firewall_az(ctx)

    ctx = NetworkFirewallContext()
    filters = ctx.container_details['container/a']['ContainerMonitoringConfigurations'][0]
    filters['AttributeFilters'][0]['Value'] = ''
    with pytest.raises(NoData, match='resource filter is invalid'):
        network_firewall.resource_filter_count(ctx)


def test_network_firewall_checks_are_catalog_selected_and_registered():
    assert len(network_firewall.ALL_CHECKS) == 25
    assert {('network-firewall', code) for code, _name, _check
            in network_firewall.ALL_CHECKS} <= custom_keys()

    context = Mock(quotas={('network-firewall', 'L-56D4232F'): {}})
    context.run.return_value = []
    assert network_firewall.get_current_quotastatus_network_firewall(ctx=context) == []
    selected = context.run.call_args.args[1]
    assert [code for code, _name, _check in selected] == [
        'L-DE163D32', 'L-0814492B', 'L-EAE8E19E', 'L-2D7A0EE2', 'L-801F8132',
        'L-56D4232F',
    ]


def test_network_firewall_configuration_checks_have_read_permissions():
    for action in (
        'ListFirewalls', 'DescribeFirewall', 'ListFirewallPolicies',
        'DescribeFirewallPolicy', 'ListRuleGroups', 'DescribeRuleGroup',
        'ListTLSInspectionConfigurations', 'DescribeTLSInspectionConfiguration',
        'ListVpcEndpointAssociations', 'DescribeVpcEndpointAssociation',
        'ListContainerAssociations', 'DescribeContainerAssociation',
    ):
        assert grants(f'network-firewall:{action}')
