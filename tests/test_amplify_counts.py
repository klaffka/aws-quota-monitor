from unittest.mock import Mock

from modules.qmchecks.amplify import CHECKS


def test_amplify_child_counts_are_maximum_per_app():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'appId': 'a'}, {'appId': 'b'}],
        [{'branchName': 'main'}],
        [{'branchName': 'main'}, {'branchName': 'dev'}],
    ]
    result = CHECKS[2][2](ctx)
    assert (result['usage'], result['resource_id']) == (2, 'b')
