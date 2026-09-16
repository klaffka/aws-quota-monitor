from unittest.mock import Mock

from modules.qmchecks.ses import CHECKS


def test_ba_ses_configuration_sets_are_counted():
    ctx = Mock()
    ctx.call.return_value = ['default', 'tracking']
    assert CHECKS[1][2](ctx)['usage'] == 2
