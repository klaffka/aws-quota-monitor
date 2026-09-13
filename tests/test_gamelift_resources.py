from unittest.mock import Mock

from modules.qmchecks.gamelift import CHECKS


def test_gamelift_resource_lists_are_paginated():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert [check(ctx)['usage'] for _, _, check in CHECKS] == [2] * len(CHECKS)
