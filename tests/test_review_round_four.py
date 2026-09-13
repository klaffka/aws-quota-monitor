from unittest.mock import Mock

from modules.qmchecks.cloudformation import CHECKS as CF_CHECKS
from modules.qmchecks.dataexchange import CHECKS as DX_CHECKS


def test_cloudformation_stack_instances_are_maximum_per_stack_set():
    ctx = Mock()
    ctx.call.side_effect = [[{'StackSetName': 'set'}], [{'StackId': 'instance'}]]
    result = CF_CHECKS[-1][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'set')


def test_dataexchange_event_actions_are_account_count():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'action'}]
    assert DX_CHECKS[1][2](ctx)['usage'] == 1
