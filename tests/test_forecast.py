from unittest.mock import Mock

from modules.qmchecks.forecast import CHECKS


def test_forecast_resource_checks_use_paginated_output_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in CHECKS[2:])
    ctx.call.return_value = [{'IsAutoPredictor': True}, {'IsAutoPredictor': False}]
    assert CHECKS[0][2](ctx)['usage'] == 2
    assert CHECKS[1][2](ctx)['usage'] == 1
