from unittest.mock import Mock
from modules.qmchecks.misc_counts import get_current_quotastatus_misc
from modules.qmchecks.workspaces import CHECKS

def test_s_to_z_misc_resource_counts():
    ctx = Mock(quotas={('social-messaging', 'L-8479D5F2'): {}, ('ssm-quicksetup', 'L-D1C554CF'): {}, ('ssm-sap', 'L-C8103580'): {}})
    ctx.run.side_effect = lambda service, checks, skip: [checks[0][2](ctx)]
    ctx.call.return_value = [{'id': 'resource'}]
    assert len(get_current_quotastatus_misc(ctx=ctx)) == 3

def test_workspaces_ip_groups_are_counted():
    ctx = Mock()
    ctx.call.return_value = [{}, {}]
    check = next(c for c in CHECKS if c[0] == 'L-0E312A12')
    assert check[2](ctx)['usage'] == 2
