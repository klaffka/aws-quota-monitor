"""AWS Network Firewall regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call('network-firewall', method, key, **kwargs)),
                source=f'network-firewall:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-DE163D32', 'Firewalls',
     lambda ctx: resource_count(ctx, 'list_firewalls', 'Firewalls')),
    ('L-0814492B', 'Firewall policies',
     lambda ctx: resource_count(ctx, 'list_firewall_policies', 'FirewallPolicies')),
    ('L-EAE8E19', 'Stateless rulegroups',
     lambda ctx: resource_count(ctx, 'list_rule_groups', 'RuleGroups', Type='STATELESS')),
    ('L-2D7A0EE2', 'Stateful rulegroups',
     lambda ctx: resource_count(ctx, 'list_rule_groups', 'RuleGroups', Type='STATEFUL')),
    ('L-801F8132', 'TLS configurations',
     lambda ctx: resource_count(ctx, 'list_tls_inspection_configurations', 'TLSInspectionConfigurations')),
]


def get_current_quotastatus_network_firewall(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'network-firewall' for service, _ in context.quotas):
        return []
    return context.run('network-firewall', CHECKS, skip)
