from unittest.mock import Mock

from modules.qmchecks.connect import CHECKS as CONNECT_CHECKS
from modules.qmchecks.ses import CHECKS as SES_CHECKS


def test_ses_tenants_are_counted_from_paginated_v2_inventory():
    ctx = Mock()
    ctx.call.return_value = [{'TenantName': 'one'}, {'TenantName': 'two'}]
    assert SES_CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.args[:3] == ('sesv2', 'list_tenants', 'Tenants')


def test_connect_instances_are_counted_from_paginated_inventory():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'one'}, {'Id': 'two'}]
    assert CONNECT_CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.args[:3] == ('connect', 'list_instances', 'InstanceSummaryList')
