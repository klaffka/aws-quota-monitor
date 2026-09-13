from unittest.mock import Mock
from modules.qmchecks.directconnect import CHECKS

def test_directconnect_scoped_counts():
    ctx = Mock()
    def call(service, method, key, **kwargs):
        if method == 'describe_connections':
            return [{'connectionId': 'a', 'location': 'x'}, {'connectionId': 'b', 'location': 'x'}, {'connectionId': 'c', 'location': 'y'}]
        return [{'virtualInterfaceId': 'v1'}, {'virtualInterfaceId': 'v2'}] if kwargs['connectionId'] == 'b' else [{'virtualInterfaceId': 'v'}]
    ctx.call.side_effect = call
    assert next(c for c in CHECKS if c[0] == 'L-A2659207')[2](ctx)['usage'] == 2
    assert next(c for c in CHECKS if c[0] == 'L-53A26B6D')[2](ctx)['usage'] == 2
