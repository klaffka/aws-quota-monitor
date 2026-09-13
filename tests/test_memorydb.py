from unittest.mock import Mock

from modules.qmchecks.memorydb import CHECKS


def test_memorydb_counts_nodes_and_resources():
    ctx = Mock()
    cluster = {'Name': 'c1', 'Shards': [
        {'NumberOfNodes': 2}, {'NumberOfNodes': 1},
    ]}
    ctx.call.return_value = [cluster]
    assert CHECKS[0][2](ctx)['usage'] == 3
    assert CHECKS[1][2](ctx)['usage'] == 3
    ctx.call.return_value = [{'Name': 'u', 'UserNames': ['user']}]
    assert CHECKS[2][2](ctx)['usage'] == 1
    assert CHECKS[3][2](ctx)['usage'] == 1
    ctx.call.return_value = [{'Name': 'user'}]
    assert CHECKS[4][2](ctx)['usage'] == 1
    ctx.call.return_value = [{'Name': 'subnet', 'Subnets': [{}]}]
    assert CHECKS[5][2](ctx)['usage'] == 1
    assert CHECKS[6][2](ctx)['usage'] == 1
    ctx.call.return_value = [{'Name': 'param'}]
    assert CHECKS[7][2](ctx)['usage'] == 1
