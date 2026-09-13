from unittest.mock import Mock
from modules.qmchecks.ec2.ec2 import CHECKS

def test_ec2_network_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'TransitGatewayId': 't'}], [{'CustomerGatewayId': 'c'}, {'CustomerGatewayId': 'd'}], [{'VpnGatewayId': 'v'}]]
    checks = [c for c in CHECKS if c[0] in {'L-A2478D36', 'L-4FB7FF5D', 'L-7029FAB6'}]
    assert [c[2](ctx)['usage'] for c in checks] == [1, 2, 1]
