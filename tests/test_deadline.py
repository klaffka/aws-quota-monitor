from unittest.mock import Mock

from modules.qmchecks.deadline import CHECKS, per_farm


def test_deadline_account_counts_use_paginated_output_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS[:3])


def test_deadline_per_farm_count_uses_maximum():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'farmId': 'farm-1'}, {'farmId': 'farm-2'}],
        [{'id': 'one'}],
        [{'id': 'one'}, {'id': 'two'}],
    ]
    result = per_farm(ctx, 'list_fleets', 'fleets')
    assert (result['usage'], result['resource_id']) == (2, 'farm-2')
