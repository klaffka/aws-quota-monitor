from unittest.mock import Mock

from modules.qmchecks.cloudformation import stack_sets, stacks, types


def test_cloudformation_stack_inventory_excludes_deleted_history():
    ctx = Mock()
    ctx.call.return_value = [
        {'StackName': 'active', 'StackStatus': 'CREATE_COMPLETE'},
        {'StackName': 'failed', 'StackStatus': 'DELETE_FAILED'},
        {'StackName': 'deleted', 'StackStatus': 'DELETE_COMPLETE'},
    ]
    assert [stack['StackName'] for stack in stacks(ctx)] == ['active', 'failed']
    assert ctx.call.call_args.args[:3] == ('cloudformation', 'list_stacks', 'StackSummaries')


def test_cloudformation_stack_sets_use_active_filtered_inventory():
    ctx = Mock()
    ctx.call.return_value = [{'StackSetName': 'one'}, {'StackSetName': 'two'}, {'StackSetName': 'one'}]
    assert len(stack_sets(ctx)) == 2
    assert ctx.call.call_args.kwargs == {'Status': 'ACTIVE'}


def test_cloudformation_module_and_hook_counts_are_private_types():
    ctx = Mock()
    ctx.call.return_value = [{'TypeName': 'x'}, {'TypeName': 'public', 'IsActivated': True}]
    assert len(types(ctx, 'MODULE')) == 1
    assert ctx.call.call_args.kwargs == {'Type': 'MODULE', 'Visibility': 'PRIVATE', 'DeprecatedStatus': 'LIVE'}
