from unittest.mock import Mock

from modules.qmchecks.macie import CHECKS as MACIE_CHECKS
from modules.qmchecks.securityhub import CHECKS as HUB_CHECKS


def test_macie_members_and_invitations():
    ctx = Mock()
    ctx.call.side_effect = [[{}, {}], {'invitationsCount': 1}]
    assert MACIE_CHECKS[2][2](ctx)['usage'] == 2
    assert MACIE_CHECKS[3][2](ctx)['usage'] == 1


def test_securityhub_outstanding_invitations():
    ctx = Mock()
    ctx.call.return_value = {'InvitationsCount': 3}
    assert HUB_CHECKS[-1][2](ctx)['usage'] == 3
