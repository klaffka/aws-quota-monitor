from unittest.mock import Mock

from modules.qmchecks.codedeploy import CHECKS as DEPLOY_CHECKS
from modules.qmchecks.codeguruprofiler import CHECKS as PROFILER_CHECKS


def test_codedeploy_counts_apps_and_max_groups():
    ctx = Mock()
    ctx.call.side_effect = [
        ['app1', 'app2'],
        ['g1', 'g2'],
        ['g3'],
    ]
    assert DEPLOY_CHECKS[0][2](ctx)['usage'] == 2
    # Fresh response for the per-application inventory.
    ctx.call.side_effect = [['app1', 'app2'], ['g1', 'g2'], ['g3']]
    assert DEPLOY_CHECKS[1][2](ctx)['usage'] == 2


def test_codeguru_profiler_counts_groups():
    ctx = Mock()
    ctx.call.return_value = ['group1', 'group2']
    assert PROFILER_CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.args[1] == 'list_profiling_groups'
