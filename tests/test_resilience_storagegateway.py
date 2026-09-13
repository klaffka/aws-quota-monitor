from unittest.mock import Mock

from modules.qmchecks.resiliencehub import CHECKS as RESILIENCE_CHECKS
from modules.qmchecks.storagegateway import per_gateway


def test_resilience_hub_counts_applications_and_policies():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert RESILIENCE_CHECKS[0][2](ctx)['usage'] == 2
    assert RESILIENCE_CHECKS[1][2](ctx)['usage'] == 2


def test_storage_gateway_counts_volumes_per_gateway_and_type():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'GatewayARN': 'gw-1'}, {'GatewayARN': 'gw-2'}],
        [{'VolumeType': 'STORED'}],
        [{'VolumeType': 'STORED'}, {'VolumeType': 'CACHED'}],
    ]
    result = per_gateway(ctx, 'list_volumes', 'VolumeInfos', 'STORED')
    assert (result['usage'], result['resource_id']) == (1, 'gw-1')
