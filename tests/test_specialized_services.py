from unittest.mock import Mock

from modules.qmchecks.specialized import cleanrooms_checks, verified_checks


def test_cleanrooms_resource_counts():
    ctx = Mock()
    checks = cleanrooms_checks(ctx)
    ctx.call.return_value = [{}]
    assert checks[0][2](ctx)['usage'] == 1
    ctx.call.return_value = [{}, {}]
    assert checks[1][2](ctx)['usage'] == 2
    ctx.call.return_value = [{}]
    assert checks[2][2](ctx)['usage'] == 1


def test_verified_permissions_templates_per_store():
    ctx = Mock()
    ctx.call.side_effect = [[{'policyStoreId': 's1'}, {'policyStoreId': 's2'}],
                            [{}, {}], [{}]]
    checks = verified_checks(ctx)
    assert checks[0][2](ctx)['usage'] == 2
    ctx.call.side_effect = [[{'policyStoreId': 's1'}, {'policyStoreId': 's2'}],
                            [{}, {}], [{}]]
    assert checks[1][2](ctx)['usage'] == 2


def test_cleanrooms_membership_scoped_quotas_use_maximum():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'm1'}, {'id': 'm2'}], [{}, {}], [{}]]
    check = cleanrooms_checks(ctx)[3][2]
    assert check(ctx)['usage'] == 2


def test_cleanrooms_invited_members_are_counted_per_collaboration():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'c1'}],
                            [{'status': 'INVITED'}, {'status': 'ACTIVE'}, {'status': 'INVITED'}]]
    checks = cleanrooms_checks(ctx)
    check = next(item[2] for item in checks if item[0] == 'L-F7B26AF5')
    assert check(ctx)['usage'] == 2
