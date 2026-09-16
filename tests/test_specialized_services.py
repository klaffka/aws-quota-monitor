from unittest.mock import Mock

from modules.qmchecks.specialized import cleanrooms_checks, verified_checks


def check_for(ctx, code):
    # Address a check by its quota code; the list order is not a contract.
    return next(item[2] for item in cleanrooms_checks(ctx) if item[0] == code)


def test_cleanrooms_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{}]
    assert check_for(ctx, 'L-F60C2030')(ctx)['usage'] == 1
    ctx.call.return_value = [{}, {}]
    assert check_for(ctx, 'L-99A163CB')(ctx)['usage'] == 2
    ctx.call.return_value = [{}]
    assert check_for(ctx, 'L-7CEACCA0')(ctx)['usage'] == 1


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
    assert check_for(ctx, 'L-AF88CE55')(ctx)['usage'] == 2


def test_cleanrooms_ongoing_queries_ask_for_each_unfinished_state():
    """ListProtectedQueries filters by one status, so ongoing costs three calls."""
    ctx = Mock()

    def call(service, method, key=None, **kwargs):
        if method == 'list_memberships':
            return [{'id': 'm1'}, {'id': 'm2'}]
        return [{}, {}] if kwargs['membershipIdentifier'] == 'm2' else [{}]

    ctx.call.side_effect = call
    # m1 runs one per state and m2 two, so the account holds nine.
    assert check_for(ctx, 'L-40165B7B')(ctx)['usage'] == 9
    result = check_for(ctx, 'L-F04AAAFE')(ctx)
    assert (result['usage'], result['resource_id']) == (6, 'm2')


def test_cleanrooms_invited_members_are_counted_per_collaboration():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'c1'}],
                            [{'status': 'INVITED'}, {'status': 'ACTIVE'}, {'status': 'INVITED'}]]
    checks = cleanrooms_checks(ctx)
    check = next(item[2] for item in checks if item[0] == 'L-F7B26AF5')
    assert check(ctx)['usage'] == 2
