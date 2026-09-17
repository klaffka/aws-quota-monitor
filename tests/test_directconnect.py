from unittest.mock import Mock

from modules.qmchecks.directconnect import CHECKS


def test_directconnect_resource_counts():
    # The hosted-connection and LAG scopes read fields of each connection and
    # are covered by tests/test_directconnect_and_batch_scopes.py.
    ctx = Mock()
    ctx.call.side_effect = [
        [{'directConnectGatewayId': 'gw'}],
        [{'lagId': 'lag'}],
        [{'connectionId': 'conn', 'location': 'eu-central-1'}],
        [{'connectionId': 'conn', 'location': 'eu-central-1'}],
        [{'virtualInterfaceId': 'vif'}],
    ]
    counted = ['L-62B7491E', 'L-42DEC0EF', 'L-A2659207', 'L-53A26B6D']
    by_code = {code: fn for code, _name, fn in CHECKS}
    assert [by_code[code](ctx)['usage'] for code in counted] == [1, 1, 1, 1]
