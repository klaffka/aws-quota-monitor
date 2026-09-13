from unittest.mock import Mock

from modules.qmchecks.autoscaling import resource_count


def test_autoscaling_inventory_counts_regional_resources():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'AutoScalingGroupName': 'one'}, {'AutoScalingGroupName': 'two'}],
        [{'LaunchConfigurationName': 'one'}],
    ]
    assert resource_count(ctx, 'describe_auto_scaling_groups', 'AutoScalingGroups')['usage'] == 2
    assert resource_count(ctx, 'describe_launch_configurations', 'LaunchConfigurations')['usage'] == 1
    assert ctx.call.call_args_list[0].args[:3] == (
        'autoscaling', 'describe_auto_scaling_groups', 'AutoScalingGroups')
