from unittest.mock import Mock

from modules.qmchecks.stepfunctions import versions_per_state_machine


def test_stepfunctions_versions_use_maximum_per_state_machine():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'stateMachineArn': 'arn:one'}, {'stateMachineArn': 'arn:two'}],
        [{'versionArn': 'v1'}, {'versionArn': 'v2'}], [{'versionArn': 'v3'}],
    ]
    result = versions_per_state_machine(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:one')
