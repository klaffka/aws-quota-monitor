from unittest.mock import Mock

from modules.qmchecks.appconfig import per_application
from modules.qmchecks.resource_groups import CHECKS as RESOURCE_GROUP_CHECKS
from modules.qmchecks.scheduler import CHECKS as SCHEDULER_CHECKS


def test_appconfig_nested_counts_use_maximum_per_application():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Id': 'app-1'}, {'Id': 'app-2'}],
        [{'Id': 'one'}],
        [{'Id': 'one'}, {'Id': 'two'}],
    ]
    result = per_application(ctx, 'list_environments', 'Items')
    assert (result['usage'], result['resource_id']) == (2, 'app-2')


def test_scheduler_and_resource_groups_use_paginated_keys():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'one'}, {'Id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for _, _, check in SCHEDULER_CHECKS)
    assert RESOURCE_GROUP_CHECKS[0][2](ctx)['usage'] == 2
