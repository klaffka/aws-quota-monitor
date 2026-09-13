from unittest.mock import Mock
from modules.qmchecks.misc_counts import get_current_quotastatus_misc

def test_iam_identity_center_counts():
    ctx = Mock(quotas={('sso', 'L-B44C7A29'): {}, ('sso', 'L-89954265'): {}, ('sso', 'L-7E1D4E33'): {}, ('sso', 'L-3C8D41A0'): {}})
    def call(service, method, key=None, **kwargs):
        if method == 'list_instances': return [{'InstanceArn': 'arn:i', 'IdentityStoreId': 'd'}]
        if method == 'list_permission_sets': return ['p1', 'p2']
        return ['u1', 'u2', 'u3']
    ctx.call.side_effect = call
    ctx.run.side_effect = lambda service, checks, skip: [check[2](ctx) for check in checks]
    assert [x['usage'] for x in get_current_quotastatus_misc(ctx=ctx)] == [2, 2, 3, 3]
