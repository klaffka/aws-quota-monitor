"""AWS Firewall Manager regional policy and managed-list quotas."""
import json
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def required(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Firewall Manager {subject} is missing {field}')
    return value


def unique(ctx, method, key, id_field, **kwargs):
    result = {}
    for item in ctx.call('fms', method, key, **kwargs):
        identity = required(item, id_field, 'inventory item')
        if identity in result and result[identity] != item:
            raise NoData('Firewall Manager inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def apps_lists(ctx):
    return unique(ctx, 'list_apps_lists', 'AppsLists', 'ListId', DefaultLists=False)


def protocols_lists(ctx):
    return unique(ctx, 'list_protocols_lists', 'ProtocolsLists', 'ListId', DefaultLists=False)


def list_maximum(items, field, resource_type, source):
    values = []
    for item in items:
        values_list = item.get(field)
        if not isinstance(values_list, list):
            raise NoData(f'Firewall Manager item has no {field} list')
        values.append((item.get('ListId') or item.get('PolicyId'), len(values_list), None))
    return maximum(values, resource_type, source)


def resource_sets(ctx):
    return unique(ctx, 'list_resource_sets', 'ResourceSets', 'Id')


def resources_per_set(ctx):
    values = []
    for item in resource_sets(ctx):
        identifier = item['Id']
        resources = ctx.call('fms', 'list_resource_set_resources', 'Items', Identifier=identifier)
        seen = set()
        for resource in resources:
            uri = required(resource, 'URI', 'resource-set item')
            account = required(resource, 'AccountId', 'resource-set item')
            seen.add((account, uri))
        values.append((identifier, len(seen), None))
    return maximum(values, 'FmsResourceSet',
                   'fms:ListResourceSets+ListResourceSetResources')


def policies(ctx):
    summaries = unique(ctx, 'list_policies', 'PolicyList', 'PolicyId')
    details = []
    for summary in summaries:
        identifier = summary['PolicyId']
        policy = ctx.call('fms', 'get_policy', PolicyId=identifier).get('Policy')
        if not isinstance(policy, dict) or policy.get('PolicyId') != identifier:
            raise NoData('Firewall Manager policy detail has a different identity')
        details.append(policy)
    return details


def policy_scope(ctx, scope):
    values = []
    for policy in policies(ctx):
        selected = set()
        for field in ('IncludeMap', 'ExcludeMap'):
            mapping = policy.get(field, {})
            if not isinstance(mapping, dict):
                raise NoData('Firewall Manager policy has an invalid scope map')
            entries = mapping.get(scope, [])
            if not isinstance(entries, list) or any(not isinstance(value, str) or not value
                                                     for value in entries):
                raise NoData('Firewall Manager policy has an invalid scope list')
            selected.update(entries)
        values.append((policy['PolicyId'], len(selected), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def managed_service_data(policy, relevant_types):
    service = policy.get('SecurityServicePolicyData')
    service_type = service.get('Type') if isinstance(service, dict) else None
    if service_type not in relevant_types:
        return service_type, None
    raw = service.get('ManagedServiceData') if isinstance(service, dict) else None
    if not isinstance(raw, str) or not raw:
        return service_type, None
    try:
        value = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise NoData('Firewall Manager managed service data is not valid JSON') from exc
    if not isinstance(value, dict):
        raise NoData('Firewall Manager managed service data is not an object')
    return service_type, value


def managed_list_maximum(ctx, service_types, fields):
    values = []
    for policy in policies(ctx):
        service_type, data = managed_service_data(policy, service_types)
        if service_type not in service_types:
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        container = data.get('awsNetworkFirewallConfig', data)
        if not isinstance(container, dict):
            raise NoData('Firewall Manager network firewall configuration is invalid')
        count = 0
        for field in fields:
            entries = container.get(field, [])
            if not isinstance(entries, list):
                raise NoData(f'Firewall Manager managed service data has invalid {field}')
            count += len(entries)
        values.append((policy['PolicyId'], count, None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def network_firewall_capacity(ctx, reference_field, expected_type):
    values = []
    for policy in policies(ctx):
        expected_types = {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'}
        service_type, data = managed_service_data(policy, expected_types)
        if service_type not in {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'}:
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        container = data.get('awsNetworkFirewallConfig', data)
        references = container.get(reference_field, []) if isinstance(container, dict) else None
        if not isinstance(references, list):
            raise NoData('Firewall Manager policy has an invalid Network Firewall reference list')
        total = 0
        seen = set()
        for reference in references:
            if not isinstance(reference, dict):
                raise NoData('Firewall Manager policy has an invalid Network Firewall reference')
            arn = reference.get('resourceARN') or reference.get('resourceArn')
            if not isinstance(arn, str) or not arn:
                raise NoData('Firewall Manager Network Firewall reference has no ARN')
            if arn in seen:
                continue
            seen.add(arn)
            response = ctx.call('network-firewall', 'describe_rule_group', RuleGroupArn=arn)
            summary = response.get('RuleGroupResponse')
            if not isinstance(summary, dict) or summary.get('RuleGroupArn') != arn \
                    or summary.get('Type') != expected_type:
                raise NoData('Network Firewall rule-group detail is inconsistent')
            capacity = summary.get('Capacity')
            if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
                raise NoData('Network Firewall rule-group capacity is invalid')
            total += capacity
        values.append((policy['PolicyId'], total, None))
    return maximum(values, 'FmsPolicy',
                   'fms:ListPolicies+GetPolicy+network-firewall:DescribeRuleGroup')


def ipv4_cidrs(value):
    if isinstance(value, dict):
        total = 0
        for key, child in value.items():
            if key == 'allowedIPV4CidrList':
                if not isinstance(child, list) or any(not isinstance(cidr, str) or not cidr
                                                       for cidr in child):
                    raise NoData('Firewall Manager policy has an invalid IPv4 CIDR list')
                total += len(child)
            else:
                total += ipv4_cidrs(child)
        return total
    if isinstance(value, list):
        return sum(ipv4_cidrs(child) for child in value)
    return 0


def network_firewall_cidrs(ctx):
    values = []
    for policy in policies(ctx):
        expected_types = {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'}
        service_type, data = managed_service_data(policy, expected_types)
        if service_type not in {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'}:
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        values.append((policy['PolicyId'], ipv4_cidrs(data), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def managed_field_maximum(ctx, service_type, field):
    values = []
    for policy in policies(ctx):
        actual_type, data = managed_service_data(policy, {service_type})
        if actual_type != service_type:
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        entries = data.get(field, [])
        if not isinstance(entries, list):
            raise NoData(f'Firewall Manager managed service data has invalid {field}')
        values.append((policy['PolicyId'], len(entries), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def wafv2_rule_groups(ctx, partner_only=False):
    values = []
    for policy in policies(ctx):
        service_type, data = managed_service_data(policy, {'WAFV2'})
        if service_type != 'WAFV2':
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        groups = []
        for field in ('preProcessRuleGroups', 'postProcessRuleGroups'):
            entries = data.get(field, [])
            if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
                raise NoData('Firewall Manager WAFV2 policy has an invalid rule-group list')
            groups.extend(entries)
        if partner_only:
            groups = [group for group in groups
                      if isinstance(group.get('managedRuleGroupIdentifier'), dict)
                      and group['managedRuleGroupIdentifier'].get('vendorName') not in {None, 'AWS'}]
        values.append((policy['PolicyId'], len(groups), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def wafv2_capacity(ctx):
    values = []
    for policy in policies(ctx):
        service_type, data = managed_service_data(policy, {'WAFV2'})
        if service_type != 'WAFV2':
            continue
        if not isinstance(data, dict):
            raise NoData('Firewall Manager policy has no managed service data')
        resource_types = policy.get('ResourceTypeList') or [policy.get('ResourceType')]
        if 'AWS::CloudFront::Distribution' in resource_types:
            raise NoData('CloudFront WAF rule-group capacity requires the us-east-1 endpoint')
        total = 0
        seen = set()
        for field in ('preProcessRuleGroups', 'postProcessRuleGroups'):
            groups = data.get(field, [])
            if not isinstance(groups, list) or any(not isinstance(group, dict) for group in groups):
                raise NoData('Firewall Manager WAFV2 policy has an invalid rule-group list')
            for group in groups:
                arn = group.get('ruleGroupArn')
                managed = group.get('managedRuleGroupIdentifier')
                if isinstance(arn, str) and arn:
                    group_key = ('custom', arn)
                    if group_key in seen:
                        continue
                    seen.add(group_key)
                    detail = ctx.call('wafv2', 'get_rule_group', ARN=arn).get('RuleGroup')
                    if not isinstance(detail, dict) or detail.get('ARN') != arn:
                        raise NoData('Firewall Manager WAF rule-group detail is inconsistent')
                    capacity = detail.get('Capacity')
                elif isinstance(managed, dict):
                    vendor = managed.get('vendorName')
                    name = managed.get('managedRuleGroupName')
                    if not isinstance(vendor, str) or not vendor or not isinstance(name, str) or not name:
                        raise NoData('Firewall Manager managed WAF rule group has no identity')
                    version = managed.get('version') if managed.get('versionEnabled') is True else None
                    if managed.get('versionEnabled') is True \
                            and (not isinstance(version, str) or not version):
                        raise NoData('Firewall Manager managed WAF rule group has no version')
                    group_key = ('managed', vendor, name, version)
                    if group_key in seen:
                        continue
                    seen.add(group_key)
                    kwargs = {'VendorName': vendor, 'Name': name, 'Scope': 'REGIONAL'}
                    if version:
                        kwargs['VersionName'] = version
                    capacity = ctx.call('wafv2', 'describe_managed_rule_group', **kwargs).get('Capacity')
                else:
                    raise NoData('Firewall Manager WAF rule group has no resolvable identity')
                if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
                    raise NoData('Firewall Manager WAF rule-group capacity is invalid')
                total += capacity
        values.append((policy['PolicyId'], total, None))
    return maximum(values, 'FmsPolicy',
                   'fms:ListPolicies+GetPolicy+wafv2:GetRuleGroup+DescribeManagedRuleGroup')


def network_acl_rules(ctx):
    values = []
    for policy in policies(ctx):
        service = policy.get('SecurityServicePolicyData')
        if not isinstance(service, dict) or service.get('Type') != 'NETWORK_ACL_COMMON':
            continue
        option = service.get('PolicyOption', {}).get('NetworkAclCommonPolicy', {})
        entries = option.get('NetworkAclEntrySet') if isinstance(option, dict) else None
        if not isinstance(entries, dict):
            raise NoData('Firewall Manager network ACL policy has no entry set')
        directions = {True: 0, False: 0}
        for field in ('FirstEntries', 'LastEntries'):
            rules = entries.get(field, [])
            if not isinstance(rules, list):
                raise NoData('Firewall Manager network ACL policy has an invalid rule list')
            for rule in rules:
                if not isinstance(rule, dict) or not isinstance(rule.get('Egress'), bool):
                    raise NoData('Firewall Manager network ACL policy has an invalid rule')
                directions[rule['Egress']] += 1
        values.append((policy['PolicyId'], max(directions.values()), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def tags_per_policy(ctx):
    values = []
    for policy in policies(ctx):
        tags = policy.get('ResourceTags', [])
        if not isinstance(tags, list) or any(not isinstance(tag, dict) or not isinstance(tag.get('Key'), str)
                                             or not isinstance(tag.get('Value'), str) for tag in tags):
            raise NoData('Firewall Manager policy has invalid resource tags')
        values.append((policy['PolicyId'], len(tags), None))
    return maximum(values, 'FmsPolicy', 'fms:ListPolicies+GetPolicy')


def admin_count(ctx):
    admins = unique(ctx, 'list_admin_accounts_for_organization', 'AdminAccounts', 'AdminAccount')
    return dict(usage=len(admins), source='fms:ListAdminAccountsForOrganization',
                method='ACCOUNT_COUNT')


def member_count(ctx):
    members = ctx.call('fms', 'list_member_accounts', 'MemberAccounts')
    if any(not isinstance(member, str) or not member for member in members):
        raise NoData('Firewall Manager member-account inventory has an invalid identity')
    return dict(usage=len(set(members)), source='fms:ListMemberAccounts', method='ACCOUNT_COUNT')

CHECKS = [
    ('L-0B28E140', 'Firewall Manager policies per organization per Region',
     lambda c: dict(usage=len(c.call('fms', 'list_policies', 'PolicyList')),
                    source='fms:ListPolicies', method='ACCOUNT_COUNT')),
    ('L-0E131699', 'Custom managed application lists per account',
     lambda c: dict(usage=len(apps_lists(c)), source='fms:ListAppsLists', method='ACCOUNT_COUNT')),
    ('L-0745D646', 'Applications per application list',
     lambda c: list_maximum(apps_lists(c), 'AppsList', 'FmsAppsList', 'fms:ListAppsLists')),
    ('L-C6CF2DBB', 'Custom managed protocol lists per account',
     lambda c: dict(usage=len(protocols_lists(c)), source='fms:ListProtocolsLists', method='ACCOUNT_COUNT')),
    ('L-742188BD', 'Protocols per protocol list',
     lambda c: list_maximum(protocols_lists(c), 'ProtocolsList', 'FmsProtocolsList', 'fms:ListProtocolsLists')),
    ('L-573ADF04', 'Resource sets per Firewall Manager admin account',
     lambda c: dict(usage=len(resource_sets(c)), source='fms:ListResourceSets', method='ACCOUNT_COUNT')),
    ('L-3F3557EB', 'Resources per resource set', resources_per_set),
    ('L-74591874', 'Admins per organization in Firewall Manager',
     admin_count),
    ('L-450C679C', 'Accounts per Firewall Manager admin', member_count),
    ('L-C80E7B9E', 'Organizational units in scope per policy per Region',
     lambda c: policy_scope(c, 'ORG_UNIT')),
    ('L-98694ACE', 'Explicitly included or excluded accounts per policy per Region',
     lambda c: policy_scope(c, 'ACCOUNT')),
    ('L-07FCB28B', 'Tags to include or exclude resources per policy', tags_per_policy),
    ('L-9E030C62', 'Stateful rule groups per Network Firewall policy',
     lambda c: managed_list_maximum(c, {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'},
                                    ('networkFirewallStatefulRuleGroupReferences',))),
    ('L-941CF907', 'Stateless rule groups per Network Firewall policy',
     lambda c: managed_list_maximum(c, {'NETWORK_FIREWALL', 'IMPORT_NETWORK_FIREWALL'},
                                    ('networkFirewallStatelessRuleGroupReferences',))),
    ('L-DE1D154D', 'Route 53 Resolver DNS Firewall rule groups per DNS Firewall policy',
     lambda c: managed_list_maximum(c, {'DNS_FIREWALL'},
                                    ('preProcessRuleGroups', 'postProcessRuleGroups'))),
    ('L-F4032167', 'IPV4 CIDRs for a Network Firewall policy', network_firewall_cidrs),
    ('L-72AC804F', 'Primary security groups per common security group policy',
     lambda c: managed_field_maximum(c, 'SECURITY_GROUPS_COMMON', 'securityGroups')),
    ('L-3BC4947E', 'Audit security groups per security group content audit policy',
     lambda c: managed_field_maximum(c, 'SECURITY_GROUPS_CONTENT_AUDIT', 'securityGroups')),
    ('L-743D9B7E', 'AWS WAF Classic rule groups per AWS WAF Classic policy',
     lambda c: managed_field_maximum(c, 'WAF', 'ruleGroups')),
    ('L-CA0A307F', 'Rule groups per AWS WAF policy', wafv2_rule_groups),
    ('L-1608788B', 'Partner rule groups per AWS WAF policy',
     lambda c: wafv2_rule_groups(c, partner_only=True)),
    ('L-7AB3A351', 'Inbound/outbound rules per network ACL policy', network_acl_rules),
    ('L-5AB0AC42', 'Stateful rule group capacity per Network Firewall policy',
     lambda c: network_firewall_capacity(c, 'networkFirewallStatefulRuleGroupReferences', 'STATEFUL')),
    ('L-7F63BF51', 'Stateless rule group capacity per Network Firewall policy',
     lambda c: network_firewall_capacity(c, 'networkFirewallStatelessRuleGroupReferences', 'STATELESS')),
    ('L-1E778CA5', 'Web ACL capacity units (WCU) used in an AWS WAF policy', wafv2_capacity),
]


def get_current_quotastatus_fms(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'fms' for service, _ in context.quotas):
        return []
    return context.run('fms', CHECKS, skip)
