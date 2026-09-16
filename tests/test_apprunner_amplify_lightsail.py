from unittest.mock import Mock

from modules.qmchecks.apprunner import CHECKS as RUNNER
from modules.qmchecks.amplify import CHECKS as AMPLIFY
from modules.qmchecks.lightsail import CHECKS as LIGHTSAIL


def test_app_runner_amplify_and_lightsail_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'ServiceName': 'service'}], [{'appId': 'app'}]]
    assert RUNNER[0][2](ctx)['usage'] == 1
    assert AMPLIFY[0][2](ctx)['usage'] == 1
    ctx.call.return_value = [{'name': 'resource'}]
    ctx.call.side_effect = None
    # The plain regional inventories; tests/test_lightsail.py covers the
    # per-resource checks, which read sizes and nested lists instead.
    counted = {'L-4259AF9B', 'L-3B2B13A1', 'L-BB561519', 'L-1DB37119', 'L-C512E6B9',
               'L-CF67FCDA', 'L-D5FCDF87'}
    assert [check[2](ctx)['usage'] for check in LIGHTSAIL
            if check[0] in counted] == [1] * len(counted)
