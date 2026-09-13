from unittest.mock import Mock

from modules.qmchecks.pcs import CHECKS as PCS
from modules.qmchecks.grafana import CHECKS as GRAFANA
from modules.qmchecks.oam import CHECKS as OAM
from modules.qmchecks.networkmonitor import CHECKS as NETWORKMONITOR
from modules.qmchecks.gameliftstreams import CHECKS as STREAMS


def test_round_three_resource_counts():
    for checks in (PCS, GRAFANA, OAM, NETWORKMONITOR):
        context = Mock()
        context.call.return_value = [{}]
        assert [check[2](context)['usage'] for check in checks] == [1] * len(checks)
    context = Mock()
    context.call.side_effect = [[{}], [{}]]
    assert [check[2](context)['usage'] for check in STREAMS] == [1, 1]
