from unittest.mock import Mock

from modules.qmchecks.network_firewall import CHECKS


def test_network_firewall_checks_use_paginated_resource_keys_and_types():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS)
    assert ctx.call.call_args_list[2].kwargs['Type'] == 'STATELESS'
    assert ctx.call.call_args_list[3].kwargs['Type'] == 'STATEFUL'
