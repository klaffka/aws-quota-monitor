from unittest.mock import Mock

from modules.qmchecks.kms import CHECKS as KMS_CHECKS
from modules.qmchecks.ssm import CHECKS as SSM_CHECKS
from modules.qmchecks.route53resolver import (
    CHECKS as RESOLVER_CHECKS, customer_rules,
)


def test_kms_key_inventory_is_paginated_by_context():
    ctx = Mock(account='123456789012', quotas={('kms', 'L-C2F1777E'): {'Value': 10, 'Unit': 'None'}})
    ctx.call.side_effect = [
        [{'KeyId': 'k1'}, {'KeyId': 'k2'}, {'KeyId': 'k3'}],
        {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
        {'KeyMetadata': {'KeyManager': 'AWS'}},
        {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
    ]
    result = KMS_CHECKS[0][2](ctx)
    assert result['usage'] == 2
    assert any(call.args[1] == 'list_keys' for call in ctx.call.call_args_list)


def test_ssm_legacy_parameters_default_to_standard_tier():
    ctx = Mock(account='123456789012', quotas={
        ('ssm', 'L-C3B871CB'): {'Value': 10, 'Unit': 'None'},
        ('ssm', 'L-527D1CD8'): {'Value': 10, 'Unit': 'None'},
    })
    ctx.call.return_value = [
        {'Name': 'legacy'}, {'Name': 'advanced', 'Tier': 'Advanced'},
        {'Name': 'standard', 'Tier': 'Standard'},
    ]
    results = {code: fn(ctx) for code, _, fn in SSM_CHECKS if ('ssm', code) in ctx.quotas}
    assert {code: result['usage'] for code, result in results.items()
            if code in {'L-C3B871CB', 'L-527D1CD8'}} == {
        'L-C3B871CB': 2, 'L-527D1CD8': 1,
    }


def test_resolver_system_rules_are_excluded():
    ctx = Mock(account='123456789012')
    ctx.call.return_value = [
        {'Id': 'r1', 'OwnerId': '123456789012'},
        {'Id': 'r2', 'OwnerId': 'route53.amazonaws.com'},
        {'Id': 'r3'},
    ]
    assert len(customer_rules(ctx)) == 2


def test_resolver_checks_use_paginated_apis():
    ctx = Mock(account='123456789012', quotas={
        ('route53resolver', 'L-4A669CC0'): {'Value': 4, 'Unit': 'None'},
        ('route53resolver', 'L-51D8A1FB'): {'Value': 10, 'Unit': 'None'},
        ('route53resolver', 'L-D2FE9758'): {'Value': 6, 'Unit': 'None'},
        ('route53resolver', 'L-D74B6237'): {'Value': 6, 'Unit': 'None'},
        ('route53resolver', 'L-94E19253'): {'Value': 10, 'Unit': 'None'},
        ('route53resolver', 'L-9FA3C0A4'): {'Value': 10, 'Unit': 'None'},
        ('route53resolver', 'L-02CC8B74'): {'Value': 10, 'Unit': 'None'},
    })
    def call(service, method, key=None, **kwargs):
        values = {
            'list_resolver_endpoints': [{'Id': 'e1', 'IpAddresses': [{}, {}]}],
            'list_resolver_rules': [{'Id': 'r1', 'OwnerId': '123456789012', 'TargetIps': [{}]}],
            'list_resolver_rule_associations': [{}],
            'list_firewall_domain_lists': [{}],
            'list_firewall_domains': [{}],
            'list_firewall_rule_groups': [{}],
        }
        return values[method]
    ctx.call.side_effect = call
    results = {code: fn(ctx) for code, _, fn in RESOLVER_CHECKS}
    assert len(results) == 8
    assert results['L-D2FE9758']['usage'] == 2
