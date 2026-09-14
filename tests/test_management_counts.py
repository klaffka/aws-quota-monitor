from unittest.mock import Mock

from modules.qmchecks.management_counts import get_current_quotastatus_management_counts
from modules.qmchecks.management_counts import cloud_map_namespace_max, cloud_map_parent_max


def test_management_resource_counts():
    ctx = Mock(quotas={('servicediscovery', 'L-0FE3F50E'): {},
                       ('servicediscovery', 'L-2DA90E5C'): {},
                       ('servicediscovery', 'L-D95E8A57'): {},
                       ('acm-pca', 'L-799883CD'): {}, ('athena', 'L-FD9D80C2'): {},
                       ('scheduler', 'L-EE5D6FF0'): {}, ('scheduler', 'L-A632CD40'): {}})
    ctx.call.side_effect = [[{}], [{}, {}], [{}], [{}, {}], [{}], [{}], [{}]]
    ctx.run.side_effect = lambda service, checks, skip: [
        {'serviceCode': service, 'quotaCode': code, 'usageValue': fn(ctx)['usage']}
        for code, _, fn in checks]
    entries = get_current_quotastatus_management_counts(ctx=ctx)
    # Scheduler quotas are handled by the dedicated scheduler collector;
    # this compatibility helper owns only the legacy service adapters.
    assert [e['usageValue'] for e in entries] == [1, 0, 0, 0, 1, 1]


def test_cloud_map_parent_inventories_are_paginated_and_scoped():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'ns-1'}],
        [{'Id': 'svc-1'}],
        [{'Id': 'instance-1'}, {'Id': 'instance-2'}],
    ]
    result = cloud_map_parent_max(ctx, 'list_instances', 'Instances')
    assert (result['usage'], result['resource_id']) == (2, 'svc-1')

    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'ns-1'}],
        [{'Id': 'svc-1'}, {'Id': 'svc-2'}],
        [{'Id': 'i-1'}],
        [{'Id': 'i-2'}, {'Id': 'i-3'}],
    ]
    result = cloud_map_namespace_max(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'ns-1')
