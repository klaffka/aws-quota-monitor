"""Route 53 Resolver quotas backed by paginated regional inventories."""
from modules.qmcore.aws import CheckContext, session_from_env, maximum


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
    return ctx.call('route53resolver', 'list_firewall_domain_lists', 'FirewallDomainLists')


def firewall_rule_groups(ctx):
    return ctx.call('route53resolver', 'list_firewall_rule_groups', 'FirewallRuleGroups')

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
]


def get_current_quotastatus_route53resolver(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'route53resolver' for service, _ in context.quotas):
        return []
    return context.run('route53resolver', CHECKS, skip)
