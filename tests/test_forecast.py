from unittest.mock import Mock

from modules.qmchecks.forecast import CHECKS

# The plain regional inventories; the parallel task counts read a status and
# the dataset group check describes each group, so both have their own tests.
COUNTED = {'L-5054D782', 'L-D613D53B', 'L-884F7F75', 'L-F58E51A9', 'L-235B11D6',
           'L-762142D9', 'L-561FC25E', 'L-928BCA42', 'L-6AD28BD9', 'L-E1AC300F',
           'L-1306EC42'}


def test_forecast_resource_checks_use_paginated_output_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2
               for code, _, check in CHECKS if code in COUNTED)
    ctx.call.return_value = [{'IsAutoPredictor': True}, {'IsAutoPredictor': False}]
    assert CHECKS[0][2](ctx)['usage'] == 2
    assert CHECKS[1][2](ctx)['usage'] == 1
