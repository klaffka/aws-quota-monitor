from unittest.mock import Mock

from modules.qmchecks.iotfleetwise import CHECKS, vehicles_per_fleet


def test_iotfleetwise_account_resource_checks_use_paginated_keys():
    # The plain account inventories; the signal catalog, campaign and state
    # template scopes read a detail call and are covered by
    # tests/test_iotfleetwise_scopes.py.
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    plain = ['L-17D821A8', 'L-8AFF6AA2', 'L-72103FA9', 'L-9EE083E6', 'L-9EDEDFF3']
    by_code = {code: fn for code, _name, fn in CHECKS}
    assert all(by_code[code](ctx)['usage'] == 2 for code in plain)


def test_iotfleetwise_vehicles_use_maximum_per_fleet():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'fleet-1'}, {'id': 'fleet-2'}],
        [{'vehicleName': 'one'}],
        [{'vehicleName': 'one'}, {'vehicleName': 'two'}],
    ]
    result = vehicles_per_fleet(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'fleet-2')
