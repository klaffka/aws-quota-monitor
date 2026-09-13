from unittest.mock import Mock

from modules.qmchecks.appintegrations import CHECKS


def test_appintegration_associations_use_parent_maxima():
    ctx = Mock()
    ctx.call.side_effect = [[{'DataIntegrationArn': 'data'}], [{'Association': 'one'}]]
    ctx.call.side_effect = [[{'Name': 'data'}], [{'Association': 'one'}]]
    result = CHECKS[3][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'data')
