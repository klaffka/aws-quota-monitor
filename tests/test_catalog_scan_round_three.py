from unittest.mock import Mock

from modules.qmchecks.pcs import CHECKS as PCS
from modules.qmchecks.grafana import CHECKS as GRAFANA
from modules.qmchecks.oam import CHECKS as OAM
from modules.qmchecks.networkmonitor import CHECKS as NETWORKMONITOR
from modules.qmchecks.gameliftstreams import CHECKS as STREAMS


def test_oam_counts_and_the_links_attached_to_each_sink():
    """The sink scope reads an ARN and follows it, so answer by method."""
    ctx = Mock()

    def calls(service, method, key=None, **kwargs):
        if method == 'list_sinks':
            return [{'Arn': 'arn:sink/one'}, {'Arn': 'arn:sink/two'}]
        if method == 'list_attached_links':
            return [{}] * (3 if kwargs['SinkIdentifier'].endswith('two') else 1)
        return [{}]

    ctx.call.side_effect = calls
    usage = {code: check(ctx)['usage'] for code, _name, check in OAM}
    assert (usage['L-92C40D6D'], usage['L-AA726EB1']) == (1, 2)
    # The second sink holds three links, the first one.
    assert usage['L-303A1B23'] == 3


def test_round_three_resource_counts():
    for checks in (PCS, GRAFANA, NETWORKMONITOR):
        context = Mock()
        context.call.return_value = [{}]
        assert [check[2](context)['usage'] for check in checks] == [1] * len(checks)
    context = Mock()
    context.call.side_effect = [[{}], [{}]]
    assert [check[2](context)['usage'] for check in STREAMS] == [1, 1]
