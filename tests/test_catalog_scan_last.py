from unittest.mock import Mock

from modules.qmchecks.kafka import CHECKS as KAFKA
from modules.qmchecks.imagebuilder import CHECKS as IMAGEBUILDER


def test_last_catalog_resource_counts():
    context = Mock()
    # The broker quota is a sum of nested Provisioned.NumberOfBrokerNodes.
    context.call.side_effect = [
        [{}], [{}], [{'Provisioned': {'NumberOfBrokerNodes': 1}}], [{}],
    ]
    assert [check[2](context)['usage'] for check in KAFKA] == [1, 1, 1, 0]
    context = Mock()
    context.call.return_value = [{'arn': 'resource'}]
    assert IMAGEBUILDER[0][2](context)['usage'] == 1
