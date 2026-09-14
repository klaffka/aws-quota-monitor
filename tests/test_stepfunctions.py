from unittest.mock import Mock

from modules.qmchecks.stepfunctions import resource_count


def test_stepfunctions_resource_inventories_are_paginated_and_counted():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'stateMachineArn': 'arn:1'}, {'stateMachineArn': 'arn:2'}],
        [{'activityArn': 'arn:a'}],
    ]
    assert resource_count(ctx, 'list_state_machines', 'stateMachines')['usage'] == 2
    assert resource_count(ctx, 'list_activities', 'activities')['usage'] == 1
    assert ctx.call.call_args_list[0].args[:3] == ('stepfunctions', 'list_state_machines', 'stateMachines')


def test_state_machine_aliases_are_maximum_per_machine():
    from modules.qmchecks.stepfunctions import aliases_per_state_machine
    ctx = Mock()
    ctx.call.side_effect = [
        [{'stateMachineArn': 'one'}, {'stateMachineArn': 'two'}],
        [{'stateMachineAliasArn': 'a'}],
        [{'stateMachineAliasArn': 'a'}, {'stateMachineAliasArn': 'b'}],
    ]
    result = aliases_per_state_machine(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'two')
