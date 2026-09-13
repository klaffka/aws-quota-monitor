from unittest.mock import Mock

from modules.qmchecks.directconnect import CHECKS


def test_directconnect_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'directConnectGatewayId': 'gw'}],
        [{'lagId': 'lag'}],
        [{'connectionId': 'conn', 'location': 'eu-central-1'}],
        [{'connectionId': 'conn', 'location': 'eu-central-1'}],
        [{'virtualInterfaceId': 'vif'}],
    ]
    assert [check[2](ctx)['usage'] for check in CHECKS] == [1, 1, 1, 1]
