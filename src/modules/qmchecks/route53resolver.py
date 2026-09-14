"""Route 53 Resolver quotas backed by paginated regional inventories."""
from collections import Counter

from modules.qmchecks.route53profiles import resources_per_profile
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def endpoints(ctx):
    return ctx.call('route53resolver', 'list_resolver_endpoints', 'ResolverEndpoints')


def rules(ctx):
    return ctx.call('route53resolver', 'list_resolver_rules', 'ResolverRules')


def customer_rules(ctx):
    # System rules are returned by ListResolverRules but do not consume the
    # customer-created regional rule quota. Older API responses may omit
    # OwnerId, in which case the returned rule is treated as customer-owned.
    return [r for r in rules(ctx) if r.get('OwnerId') in (None, ctx.account)]


def firewall_domain_lists(ctx):
    domain_lists = []
    identities = set()
    for item in ctx.call('route53resolver', 'list_firewall_domain_lists',
                         'FirewallDomainLists'):
        if not isinstance(item, dict):
            raise NoData('Route 53 Resolver domain-list inventory is invalid')
        identity = item.get('Id')
        managed_owner = item.get('ManagedOwnerName')
        if (not isinstance(identity, str) or not identity
                or (managed_owner is not None
                    and (not isinstance(managed_owner, str) or not managed_owner))):
            raise NoData('Route 53 Resolver domain list is missing required identity data')
        if identity in identities:
            raise NoData('Route 53 Resolver domain-list inventory has a duplicate')
        identities.add(identity)
        if managed_owner is None:
            domain_lists.append(item)
    return domain_lists


def firewall_rule_groups(ctx):
    groups = []
    identities = set()
    for item in ctx.call('route53resolver', 'list_firewall_rule_groups',
                         'FirewallRuleGroups'):
        if not isinstance(item, dict):
            raise NoData('Route 53 Resolver firewall-rule-group inventory is invalid')
        identity = item.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Route 53 Resolver firewall rule group is missing its identity')
        if identity in identities:
            raise NoData('Route 53 Resolver firewall-rule-group inventory has a duplicate')
        identities.add(identity)
        groups.append(item)
    return groups


def firewall_groups_per_vpc(ctx):
    counts = Counter()
    identities = set()
    valid_statuses = {'COMPLETE', 'DELETING', 'UPDATING'}
    items = ctx.call('route53resolver', 'list_firewall_rule_group_associations',
                     'FirewallRuleGroupAssociations')
    for item in items:
        if not isinstance(item, dict):
            raise NoData('Route 53 Resolver firewall association is invalid')
        identity = item.get('Id')
        group_id = item.get('FirewallRuleGroupId')
        vpc_id = item.get('VpcId')
        if (not isinstance(identity, str) or not identity
                or not isinstance(group_id, str) or not group_id
                or not isinstance(vpc_id, str) or not vpc_id
                or item.get('Status') not in valid_statuses):
            raise NoData('Route 53 Resolver firewall association is incomplete')
        if identity in identities:
            raise NoData('Route 53 Resolver firewall-association inventory has a duplicate')
        identities.add(identity)
        counts[vpc_id] += 1
    return maximum(((vpc_id, count, None) for vpc_id, count in counts.items()),
                   'VPC', 'route53resolver:ListFirewallRuleGroupAssociations')


def firewall_rules_per_group(ctx):
    values = []
    for group in firewall_rule_groups(ctx):
        group_id = group['Id']
        priorities = set()
        rules = ctx.call('route53resolver', 'list_firewall_rules', 'FirewallRules',
                         FirewallRuleGroupId=group_id)
        for rule in rules:
            priority = rule.get('Priority') if isinstance(rule, dict) else None
            if (not isinstance(rule, dict)
                    or rule.get('FirewallRuleGroupId') != group_id
                    or isinstance(priority, bool) or not isinstance(priority, int)
                    or priority < 0):
                raise NoData('Route 53 Resolver firewall rule is inconsistent')
            if priority in priorities:
                raise NoData('Route 53 Resolver firewall-rule inventory has a duplicate')
            priorities.add(priority)
        values.append((group_id, len(priorities), None))
    return maximum(values, 'ResolverDNSFirewallRuleGroup',
                   'route53resolver:ListFirewallRules')

def firewall_domains(ctx):
    return [domain for domain_list in firewall_domain_lists(ctx)
            for domain in ctx.call('route53resolver', 'list_firewall_domains', 'Domains',
                                   FirewallDomainListId=domain_list.get('Id'))]


CHECKS = [
    ('L-4A669CC0', 'Maximum number of resolver endpoints per AWS Region',
     lambda ctx: dict(usage=len(endpoints(ctx)), source='route53resolver:ListResolverEndpoints', method='ACCOUNT_COUNT')),
    ('L-51D8A1FB', 'Resolver rules per AWS Region',
     lambda ctx: dict(usage=len(customer_rules(ctx)), source='route53resolver:ListResolverRules', method='ACCOUNT_COUNT')),
    ('L-D2FE9758', 'IP addresses per resolver endpoint',
     lambda ctx: maximum([(e.get('Id'), len(e.get('IpAddresses', [])), None)
                          for e in endpoints(ctx)], 'ResolverEndpoint', 'route53resolver:ListResolverEndpoints')),
    ('L-D74B6237', 'Target IP addresses per resolver rule',
     lambda ctx: maximum([(r.get('Id'), len(r.get('TargetIps', [])), None)
                          for r in customer_rules(ctx)], 'ResolverRule', 'route53resolver:ListResolverRules')),
    ('L-94E19253', 'Associations between resolver rules and VPCs per AWS Region',
     lambda ctx: dict(usage=len(ctx.call('route53resolver', 'list_resolver_rule_associations',
                                         'ResolverRuleAssociations')),
                      source='route53resolver:ListResolverRuleAssociations', method='ACCOUNT_COUNT')),
    ('L-9FA3C0A4', 'Domain lists per account',
     lambda ctx: dict(usage=len(firewall_domain_lists(ctx)), source='route53resolver:ListFirewallDomainLists', method='ACCOUNT_COUNT')),
    ('L-740A4B31', 'Domains per account',
     lambda ctx: dict(usage=len(firewall_domains(ctx)), source='route53resolver:ListFirewallDomains', method='ACCOUNT_COUNT')),
    ('L-02CC8B74', 'DNS Firewall rules groups per Region',
     lambda ctx: dict(usage=len(firewall_rule_groups(ctx)), source='route53resolver:ListFirewallRuleGroups', method='ACCOUNT_COUNT')),
    ('L-15219E1D', 'DNS Firewall rule group associations per VPC',
     firewall_groups_per_vpc),
    ('L-8B4B9B75', 'Resolver rule associations to a Route 53 Profile',
     lambda ctx: resources_per_profile(ctx, 'RESOLVER_RULE')),
    ('L-F763F4D9', 'Rules in a DNS Firewall rule group',
     firewall_rules_per_group),
    ('L-F8A07EF1', 'DNS Firewall rule groups associations to a Route 53 Profile',
     lambda ctx: resources_per_profile(ctx, 'FIREWALL_RULE_GROUP')),
]


def get_current_quotastatus_route53resolver(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'route53resolver' for service, _ in context.quotas):
        return []
    return context.run('route53resolver', CHECKS, skip)
