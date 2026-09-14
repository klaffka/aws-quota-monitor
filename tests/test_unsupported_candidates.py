from unittest.mock import Mock

from modules.qmchecks.fms import CHECKS as FMS
from modules.qmchecks.kafkaconnect import CHECKS as KAFKACONNECT
from modules.qmchecks.rolesanywhere import CHECKS as ROLESANYWHERE


def test_remaining_resource_count_candidates():
    context = Mock()
    context.call.return_value = [{}]
    assert FMS[0][2](context)['usage'] == 1
    for checks in (KAFKACONNECT, ROLESANYWHERE):
        context = Mock()
        context.call.side_effect = [[{}]] * len(checks)
        assert [check[2](context)['usage'] for check in checks] == [1] * len(checks)
