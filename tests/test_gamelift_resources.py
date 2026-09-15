from unittest.mock import Mock

from modules.qmchecks.gamelift import CHECKS

# The fleet-, group- and queue-scoped checks filter or descend, so they are
# covered by tests/test_gamelift_macie_inventories.py against a real client.
FLAT = {'L-8D885299', 'L-90D24F1B', 'L-22451070', 'L-AED4A06A', 'L-293B0017',
        'L-C6F4238C', 'L-73F6E300', 'L-8AE49BBD'}


def test_gamelift_resource_lists_are_paginated():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    usages = [check(ctx)['usage'] for code, _name, check in CHECKS if code in FLAT]
    assert usages == [2] * len(FLAT)
