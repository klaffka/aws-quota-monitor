from unittest.mock import Mock

from modules.qmchecks.workspaces_web import CHECKS


def test_workspaces_web_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}]] * 9
    assert [fn(ctx)['usage'] for _, _, fn in CHECKS[:9]] == [1] * 9


def test_workspaces_web_parent_scoped_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'portalArn': 'p1'}], [{}, {}]]
    assert CHECKS[9][2](ctx)['usage'] == 2
    ctx.call.side_effect = [[{'trustStoreArn': 't1'}], [{}, {}, {}]]
    assert CHECKS[10][2](ctx)['usage'] == 3
