from unittest.mock import Mock

from modules.qmchecks.iotfleetwise import CHECKS, vehicles_per_fleet


def test_iotfleetwise_account_resource_checks_use_paginated_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS[1:])


def test_iotfleetwise_vehicles_use_maximum_per_fleet():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'fleet-1'}, {'id': 'fleet-2'}],
        [{'vehicleName': 'one'}],
        [{'vehicleName': 'one'}, {'vehicleName': 'two'}],
    ]
    result = vehicles_per_fleet(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'fleet-2')
