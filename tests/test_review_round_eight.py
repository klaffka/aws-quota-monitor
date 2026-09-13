from unittest.mock import Mock

from modules.qmchecks.appstream import CHECKS


def test_appstream_builder_quotas_use_account_inventories():
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'builder'}]
    assert CHECKS[4][2](ctx)['usage'] == 1
    assert CHECKS[5][2](ctx)['usage'] == 1
