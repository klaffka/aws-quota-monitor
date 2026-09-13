from unittest.mock import Mock

from modules.qmchecks.datazone import CHECKS


def test_datazone_git_connections_are_maximum_per_project():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'domain'}], [{'id': 'project'}], [{'id': 'connection'}]]
    result = CHECKS[-1][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'project')
