"""AWS Network Firewall regional resource and configuration quotas."""
from collections import Counter
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


SERVICE = 'network-firewall'


def unique(items, field, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'Network Firewall {subject} inventory contains an invalid item')
        identity = item.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'Network Firewall {subject} is missing {field}')
        if identity in result and result[identity] != item:
            raise NoData(f'Network Firewall {subject} inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def inventory(ctx, method, key, field, subject, **kwargs):
    return unique(ctx.call(SERVICE, method, key, **kwargs), field, subject)


def account_count(items, source):
    return dict(usage=len(items), source=source, method='ACCOUNT_COUNT')


def list_field(value, field, subject):
    if not isinstance(value, dict):
        raise NoData(f'Network Firewall {subject} detail is invalid')
    items = value.get(field, [])
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise NoData(f'Network Firewall {subject} has an invalid {field}')
    return items


def optional_count(value, field, subject):
    count = value.get(field, 0) if isinstance(value, dict) else None
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise NoData(f'Network Firewall {subject} has an invalid {field}')
    return count


def required_count(value, field, subject):
    if not isinstance(value, dict) or field not in value:
        raise NoData(f'Network Firewall {subject} is missing {field}')
    return optional_count(value, field, subject)


def firewalls(ctx):
    return inventory(ctx, 'list_firewalls', 'Firewalls', 'FirewallArn', 'firewall')


def firewall_details(ctx):
    result = []
    for summary in firewalls(ctx):
        arn = summary['FirewallArn']
        response = ctx.call(SERVICE, 'describe_firewall', FirewallArn=arn)
        detail = response.get('Firewall') if isinstance(response, dict) else None
        if not isinstance(detail, dict) or detail.get('FirewallArn') != arn:
            raise NoData('Network Firewall firewall detail is inconsistent')
        result.append(detail)
    return result


def policies(ctx):
    return inventory(ctx, 'list_firewall_policies', 'FirewallPolicies', 'Arn',
                     'firewall policy')


def policy_details(ctx):
    result = []
    for summary in policies(ctx):
        arn = summary['Arn']
        response = ctx.call(SERVICE, 'describe_firewall_policy', FirewallPolicyArn=arn)
        config = response.get('FirewallPolicy') if isinstance(response, dict) else None
        detail = response.get('FirewallPolicyResponse') if isinstance(response, dict) else None
        if (not isinstance(config, dict) or not isinstance(detail, dict)
                or detail.get('FirewallPolicyArn') != arn):
            raise NoData('Network Firewall firewall-policy detail is inconsistent')
        result.append((arn, config, detail))
    return result


def rule_groups(ctx, group_type):
    summaries = inventory(ctx, 'list_rule_groups', 'RuleGroups', 'Arn', 'rule group',
                          Scope='ACCOUNT', Type=group_type)
    result = []
    for summary in summaries:
        arn = summary['Arn']
        response = ctx.call(SERVICE, 'describe_rule_group', RuleGroupArn=arn,
                            Type=group_type)
        config = response.get('RuleGroup') if isinstance(response, dict) else None
        detail = response.get('RuleGroupResponse') if isinstance(response, dict) else None
        if (not isinstance(config, dict) or not isinstance(detail, dict)
                or detail.get('RuleGroupArn') != arn or detail.get('Type') != group_type):
            raise NoData('Network Firewall rule-group detail is inconsistent')
        result.append((arn, config, detail))
    return result


def tls_configurations(ctx):
    return inventory(ctx, 'list_tls_inspection_configurations',
                     'TLSInspectionConfigurations', 'Arn', 'TLS configuration')


def tls_details(ctx):
    result = []
    for summary in tls_configurations(ctx):
        arn = summary['Arn']
        response = ctx.call(SERVICE, 'describe_tls_inspection_configuration',
                            TLSInspectionConfigurationArn=arn)
        config = response.get('TLSInspectionConfiguration') if isinstance(response, dict) else None
        detail = (response.get('TLSInspectionConfigurationResponse')
                  if isinstance(response, dict) else None)
        if (not isinstance(config, dict) or not isinstance(detail, dict)
                or detail.get('TLSInspectionConfigurationArn') != arn):
            raise NoData('Network Firewall TLS-configuration detail is inconsistent')
        result.append((arn, config, detail))
    return result


def container_associations(ctx):
    return inventory(ctx, 'list_container_associations', 'ContainerAssociations', 'Arn',
                     'container association')


def container_details(ctx):
    result = []
    for summary in container_associations(ctx):
        arn = summary['Arn']
        detail = ctx.call(SERVICE, 'describe_container_association',
                          ContainerAssociationArn=arn)
        if not isinstance(detail, dict) or detail.get('ContainerAssociationArn') != arn:
            raise NoData('Network Firewall container-association detail is inconsistent')
        result.append(detail)
    return result


def firewall_count(ctx):
    return account_count(firewalls(ctx), 'network-firewall:ListFirewalls')


def policy_count(ctx):
    return account_count(policies(ctx), 'network-firewall:ListFirewallPolicies')


def rule_group_count(ctx, group_type):
    return account_count(
        inventory(ctx, 'list_rule_groups', 'RuleGroups', 'Arn', 'rule group',
                  Scope='ACCOUNT', Type=group_type),
        'network-firewall:ListRuleGroups')


def tls_count(ctx):
    return account_count(tls_configurations(ctx),
                         'network-firewall:ListTLSInspectionConfigurations')


def container_count(ctx):
    return account_count(container_associations(ctx),
                         'network-firewall:ListContainerAssociations')


def policy_response_maximum(ctx, field):
    values = [(arn, optional_count(detail, field, 'firewall policy'), None)
              for arn, _config, detail in policy_details(ctx)]
    return maximum(values, 'NetworkFirewallPolicy',
                   'network-firewall:ListFirewallPolicies+DescribeFirewallPolicy')


def policy_list_maximum(ctx, field):
    values = []
    for arn, config, _detail in policy_details(ctx):
        references = list_field(config, field, 'firewall policy')
        identities = set()
        for reference in references:
            resource_arn = reference.get('ResourceArn')
            if not isinstance(resource_arn, str) or not resource_arn or resource_arn in identities:
                raise NoData(f'Network Firewall firewall policy has invalid {field}')
            identities.add(resource_arn)
        values.append((arn, len(identities), None))
    return maximum(values, 'NetworkFirewallPolicy',
                   'network-firewall:ListFirewallPolicies+DescribeFirewallPolicy')


def tls_per_policy(ctx):
    values = []
    for arn, config, _detail in policy_details(ctx):
        tls_arn = config.get('TLSInspectionConfigurationArn')
        if tls_arn is not None and (not isinstance(tls_arn, str) or not tls_arn):
            raise NoData('Network Firewall firewall policy has an invalid TLS reference')
        values.append((arn, int(tls_arn is not None), None))
    return maximum(values, 'NetworkFirewallPolicy',
                   'network-firewall:ListFirewallPolicies+DescribeFirewallPolicy')


def required_policy_per_firewall(ctx):
    values = []
    for detail in firewall_details(ctx):
        policy_arn = detail.get('FirewallPolicyArn')
        if not isinstance(policy_arn, str) or not policy_arn:
            raise NoData('Network Firewall firewall is missing its policy ARN')
        values.append((detail['FirewallArn'], 1, None))
    return maximum(values, 'NetworkFirewall',
                   'network-firewall:ListFirewalls+DescribeFirewall')


def policies_per_reference(ctx, reference_type):
    counts = Counter()
    for _arn, config, _detail in policy_details(ctx):
        references = list_field(config, reference_type, 'firewall policy')
        policy_references = set()
        for reference in references:
            resource_arn = reference.get('ResourceArn')
            if (not isinstance(resource_arn, str) or not resource_arn
                    or resource_arn in policy_references):
                raise NoData(f'Network Firewall firewall policy has invalid {reference_type}')
            policy_references.add(resource_arn)
        counts.update(policy_references)
    values = [(arn, count, None) for arn, count in counts.items()]
    return maximum(values, 'NetworkFirewallRuleGroup',
                   'network-firewall:ListFirewallPolicies+DescribeFirewallPolicy')


def policies_per_rule_group(ctx):
    stateful = policies_per_reference(ctx, 'StatefulRuleGroupReferences')
    stateless = policies_per_reference(ctx, 'StatelessRuleGroupReferences')
    return max((stateful, stateless), key=lambda result: result['usage'])


def policies_per_tls_configuration(ctx):
    counts = Counter()
    for _arn, config, _detail in policy_details(ctx):
        tls_arn = config.get('TLSInspectionConfigurationArn')
        if tls_arn is not None:
            if not isinstance(tls_arn, str) or not tls_arn:
                raise NoData('Network Firewall firewall policy has an invalid TLS reference')
            counts[tls_arn] += 1
    return maximum([(arn, count, None) for arn, count in counts.items()],
                   'NetworkFirewallTLSConfiguration',
                   'network-firewall:ListFirewallPolicies+DescribeFirewallPolicy')


def rule_group_maximum(ctx, group_type, field):
    values = []
    for arn, config, detail in rule_groups(ctx, group_type):
        if field == 'Capacity':
            usage = required_count(detail, 'Capacity', 'rule group')
        elif field == 'IPSetReferences':
            reference_sets = config.get('ReferenceSets', {})
            if not isinstance(reference_sets, dict):
                raise NoData('Network Firewall rule group has invalid reference sets')
            references = reference_sets.get('IPSetReferences', {})
            if (not isinstance(references, dict)
                    or any(not isinstance(key, str) or not key for key in references)):
                raise NoData('Network Firewall rule group has invalid IP set references')
            usage = len(references)
        else:
            rules_source = config.get('RulesSource')
            if not isinstance(rules_source, dict):
                raise NoData('Network Firewall rule group has an invalid RulesSource')
            if field == 'RulesString':
                rules = rules_source.get('RulesString', '')
                if not isinstance(rules, str):
                    raise NoData('Network Firewall rule group has an invalid RulesString')
                usage = len(rules.encode('utf-8'))
            else:
                stateless = rules_source.get('StatelessRulesAndCustomActions', {})
                if not isinstance(stateless, dict):
                    raise NoData('Network Firewall rule group has invalid stateless rules')
                usage = len(list_field(stateless, 'CustomActions', 'stateless rule group'))
        values.append((arn, usage, None))
    return maximum(values, 'NetworkFirewallRuleGroup',
                   'network-firewall:ListRuleGroups+DescribeRuleGroup')


def tls_certificate_maximum(ctx, field):
    values = []
    for arn, config, _detail in tls_details(ctx):
        configurations = list_field(config, 'ServerCertificateConfigurations',
                                    'TLS configuration')
        if field == 'ServerCertificates':
            usage = sum(len(list_field(item, field, 'server certificate configuration'))
                        for item in configurations)
        else:
            authorities = [item.get('CertificateAuthorityArn') for item in configurations]
            if any(value is not None and (not isinstance(value, str) or not value)
                   for value in authorities):
                raise NoData('Network Firewall TLS configuration has an invalid CA certificate')
            usage = sum(value is not None for value in authorities)
        values.append((arn, usage, None))
    return maximum(values, 'NetworkFirewallTLSConfiguration',
                   'network-firewall:ListTLSInspectionConfigurations+'
                   'DescribeTLSInspectionConfiguration')


def vpc_endpoint_associations(ctx):
    return inventory(ctx, 'list_vpc_endpoint_associations', 'VpcEndpointAssociations',
                     'VpcEndpointAssociationArn', 'VPC endpoint association')


def vpc_endpoint_count(ctx):
    return account_count(vpc_endpoint_associations(ctx),
                         'network-firewall:ListVpcEndpointAssociations')


def vpc_endpoints_per_firewall_az(ctx):
    counts = Counter()
    for summary in vpc_endpoint_associations(ctx):
        arn = summary['VpcEndpointAssociationArn']
        response = ctx.call(SERVICE, 'describe_vpc_endpoint_association',
                            VpcEndpointAssociationArn=arn)
        detail = response.get('VpcEndpointAssociation') if isinstance(response, dict) else None
        status = (response.get('VpcEndpointAssociationStatus')
                  if isinstance(response, dict) else None)
        if not isinstance(detail, dict) or detail.get('VpcEndpointAssociationArn') != arn:
            raise NoData('Network Firewall VPC endpoint-association detail is inconsistent')
        firewall_arn = detail.get('FirewallArn')
        states = status.get('AssociationSyncState') if isinstance(status, dict) else None
        if (not isinstance(firewall_arn, str) or not firewall_arn
                or not isinstance(states, dict) or not states
                or any(not isinstance(az, str) or not az for az in states)):
            raise NoData('Network Firewall VPC endpoint association has invalid scope data')
        for az in states:
            counts[(firewall_arn, az)] += 1
    values = [(f'{firewall_arn}/{az}', count, None)
              for (firewall_arn, az), count in counts.items()]
    return maximum(values, 'NetworkFirewallAvailabilityZone',
                   'network-firewall:ListVpcEndpointAssociations+'
                   'DescribeVpcEndpointAssociation')


def resource_filter_count(ctx):
    count = 0
    for detail in container_details(ctx):
        configurations = list_field(detail, 'ContainerMonitoringConfigurations',
                                    'container association')
        for configuration in configurations:
            filters = list_field(configuration, 'AttributeFilters',
                                 'container monitoring configuration')
            for item in filters:
                if (not isinstance(item.get('Key'), str) or not item.get('Key')
                        or not isinstance(item.get('Value'), str) or not item.get('Value')):
                    raise NoData('Network Firewall container resource filter is invalid')
            count += len(filters)
    return dict(usage=count,
                source='network-firewall:ListContainerAssociations+'
                       'DescribeContainerAssociation', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-DE163D32', 'Firewalls', firewall_count),
    ('L-0814492B', 'Firewall policies', policy_count),
    ('L-EAE8E19E', 'Stateless rulegroups',
     partial(rule_group_count, group_type='STATELESS')),
    ('L-2D7A0EE2', 'Stateful rulegroups',
     partial(rule_group_count, group_type='STATEFUL')),
    ('L-801F8132', 'TLS configurations', tls_count),
]


EXTENDED_CHECKS = [
    ('L-00042DEC', 'Number of firewalls that can use the same policy',
     partial(policy_response_maximum, field='NumberOfAssociations')),
    ('L-0E2A97AD', 'Stateless rule group capacity',
     partial(rule_group_maximum, group_type='STATELESS', field='Capacity')),
    ('L-218BF7D1', 'Server certificates per TLS configuration',
     partial(tls_certificate_maximum, field='ServerCertificates')),
    ('L-3E253D9A', 'IP set references per Suricata compatible stateful rule group',
     partial(rule_group_maximum, group_type='STATEFUL', field='IPSetReferences')),
    ('L-3EF9089F', 'VPC endpoint associations', vpc_endpoint_count),
    ('L-4BA822BD', 'Number of policies using a TLS inspection configuration',
     policies_per_tls_configuration),
    ('L-4F6C862E', 'TLS inspection configurations per policy', tls_per_policy),
    ('L-52ACCE4C', 'CA certificates per TLS configuration',
     partial(tls_certificate_maximum, field='CertificateAuthorityArn')),
    ('L-53DEAFE0', 'Stateless rules per policy',
     partial(policy_response_maximum, field='ConsumedStatelessRuleCapacity')),
    ('L-56D4232F', 'Container associations', container_count),
    ('L-5BF9763F', 'VPC endpoint associations per Availability Zone per Firewall',
     vpc_endpoints_per_firewall_az),
    ('L-63BF3FE7', 'Required firewall policies per firewall', required_policy_per_firewall),
    ('L-8B62609E', 'Stateless rule groups per policy',
     partial(policy_list_maximum, field='StatelessRuleGroupReferences')),
    ('L-9B335747', 'Stateful rule groups per policy',
     partial(policy_list_maximum, field='StatefulRuleGroupReferences')),
    ('L-9B5B9EFB', 'Number of policies that can use the same rule group',
     policies_per_rule_group),
    ('L-9E55B2E0', 'Suricata rules string size',
     partial(rule_group_maximum, group_type='STATEFUL', field='RulesString')),
    ('L-CEEC5053', 'Stateful rule group capacity',
     partial(rule_group_maximum, group_type='STATEFUL', field='Capacity')),
    ('L-DBC1A782', 'Resource filters', resource_filter_count),
    ('L-E65239AF', 'Stateful rules per policy',
     partial(policy_response_maximum, field='ConsumedStatefulRuleCapacity')),
    ('L-EB27A72A', 'Stateless rule group custom actions',
     partial(rule_group_maximum, group_type='STATELESS', field='CustomActions')),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_network_firewall(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS
                       if (SERVICE, check[0]) in context.quotas]
    return context.run(SERVICE, checks, skip)
