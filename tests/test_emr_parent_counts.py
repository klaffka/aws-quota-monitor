from unittest.mock import Mock

from modules.qmchecks.emr import active_instances_per_instance_group


def test_emr_active_instances_use_maximum_per_instance_group():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'cluster'}],
        [{'Id': 'group-a', 'RunningInstanceCount': 2},
         {'Id': 'group-b', 'RunningInstanceCount': 4}],
    ]
    result = active_instances_per_instance_group(ctx)
    assert (result['usage'], result['resource_id']) == (4, 'group-b')
