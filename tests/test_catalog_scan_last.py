from unittest.mock import Mock

from modules.qmchecks.kafka import CHECKS as KAFKA
from modules.qmchecks.proton import CHECKS as PROTON
from modules.qmchecks.imagebuilder import CHECKS as IMAGEBUILDER


def test_last_catalog_resource_counts():
    for checks in (KAFKA, PROTON):
        context = Mock()
        context.call.side_effect = [[{}]] * len(checks)
        # The broker quota is a sum of nested Provisioned.NumberOfBrokerNodes.
        if checks is KAFKA:
            context.call.side_effect = [[{}], [{}], [{'Provisioned': {'NumberOfBrokerNodes': 1}}], [{}]]
            assert [check[2](context)['usage'] for check in checks] == [1, 1, 1, 0]
        else:
            context.call.side_effect = [[{}], [{}], [{'Provisioned': {'NumberOfBrokerNodes': 1}}]]
            assert [check[2](context)['usage'] for check in checks] == [1] * len(checks)
    context = Mock()
    context.call.return_value = [{}]
    assert IMAGEBUILDER[0][2](context)['usage'] == 1
