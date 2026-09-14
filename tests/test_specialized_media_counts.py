from unittest.mock import Mock

def test_groundstation_dataflow_endpoint_maximum():
    from modules.qmchecks.groundstation import CHECKS
    ctx = Mock()
    ctx.call.side_effect = [[{'dataflowEndpointGroupId': 'g'}], {'endpointsDetails': [{}, {}]}]
    check = next(c for c in CHECKS if c[0] == 'L-98A63A85')
    assert check[2](ctx)['usage'] == 2

def test_mediapackage_origin_endpoint_maximum():
    from modules.qmchecks.streaming import max_endpoints_per_channel
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'c1'}, {'id': 'c2'}], [{}], [{}, {}, {}]]
    assert max_endpoints_per_channel(ctx)['usage'] == 3
