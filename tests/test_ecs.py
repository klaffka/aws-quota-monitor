from unittest.mock import Mock

from modules.qmchecks.ecs import container_instances_per_cluster, services_per_cluster, revisions_per_family


def test_ecs_services_use_maximum_per_cluster():
    ctx = Mock()
    ctx.call.side_effect = [
        ['arn:cluster:one', 'arn:cluster:two'],
        ['arn:service:1', 'arn:service:2'],
        ['arn:service:3'],
    ]
    result = services_per_cluster(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:cluster:one')


def test_ecs_revisions_count_active_and_inactive_per_family():
    ctx = Mock()
    ctx.call.side_effect = [
        ['web'],
        ['arn:web:1', 'arn:web:2'],
        ['arn:web:2', 'arn:web:3'],
    ]
    result = revisions_per_family(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'web')


def test_ecs_container_instances_use_maximum_per_cluster():
    ctx = Mock()
    ctx.call.side_effect = [['arn:cluster:one', 'arn:cluster:two'], ['i1', 'i2'], ['i3']]
    result = container_instances_per_cluster(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:cluster:one')
