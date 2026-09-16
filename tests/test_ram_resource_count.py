from unittest.mock import Mock
from modules.qmchecks.ram import CHECKS


def test_ram_resource_shares_count():
    context = Mock(); context.call.return_value = [{}]
    assert CHECKS[0][2](context)['usage'] == 1
    assert context.call.call_args.kwargs == {'resourceOwner': 'SELF'}


def test_ram_principals_and_pending_invitations_are_account_counts():
    context = Mock()
    context.call.return_value = [{}]
    assert CHECKS[1][2](context)['usage'] == 1
    assert context.call.call_args.kwargs == {'resourceOwner': 'SELF'}
    assert CHECKS[2][2](context)['usage'] == 1
    assert context.call.call_args.kwargs == {}
