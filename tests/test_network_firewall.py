from modules.qmchecks.network_firewall import CHECKS


def test_network_firewall_checks_use_paginated_resource_keys_and_types():
    class Context:
        def __init__(self):
            self.calls = []

        def call(self, service, method, key=None, **kwargs):
            self.calls.append((service, method, key, kwargs))
            fields = {
                'list_firewalls': 'FirewallArn',
                'list_firewall_policies': 'Arn',
                'list_rule_groups': 'Arn',
                'list_tls_inspection_configurations': 'Arn',
            }
            return [{fields[method]: 'one'}, {fields[method]: 'two'}]

    ctx = Context()
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS)
    assert ctx.calls[2][3] == {'Scope': 'ACCOUNT', 'Type': 'STATELESS'}
    assert ctx.calls[3][3] == {'Scope': 'ACCOUNT', 'Type': 'STATEFUL'}
    assert CHECKS[2][0] == 'L-EAE8E19E'
