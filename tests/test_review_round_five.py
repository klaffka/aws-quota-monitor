from unittest.mock import Mock

from modules.qmchecks.kms import CHECKS


def test_kms_parent_quotas_count_aliases_and_grants_per_customer_key():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'KeyId': 'key-1'}], {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
        [{'KeyId': 'key-1'}], {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
        [{'AliasName': 'alias'}],
        [{'KeyId': 'key-1'}], {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
        [{'GrantId': 'grant'}],
    ]
    assert CHECKS[1][2](ctx)['usage'] == 1
    ctx.call.side_effect = [
        [{'KeyId': 'key-1'}], {'KeyMetadata': {'KeyManager': 'CUSTOMER'}},
        [{'GrantId': 'grant'}],
    ]
    assert CHECKS[2][2](ctx)['usage'] == 1
