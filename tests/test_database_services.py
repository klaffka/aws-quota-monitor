from unittest.mock import Mock

from modules.qmchecks.dynamodb import CHECKS as DDB
from modules.qmchecks.elasticache import CHECKS as CACHE
from modules.qmchecks.docdb import CHECKS as DOCDB
from modules.qmchecks.neptune import CHECKS as NEPTUNE


def test_database_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'Resource': 'resource'}]
    assert DDB[0][2](ctx)['usage'] == 1
    # The plain ElastiCache inventories; the shard scope has its own test below.
    assert [c[2](ctx)['usage'] for c in CACHE
            if c[0] != 'L-7D6587E6'] == [1] * (len(CACHE) - 1)
    # The plain account inventories; the per-cluster, per-group and per-instance
    # scopes read a field of each entry and have their own test.
    plain = ['L-13F31459', 'L-739A3A85', 'L-02DEA053', 'L-2A542E16', 'L-F7FABF71',
             'L-B2551F83']
    by_code = {code: fn for code, _name, fn in DOCDB}
    assert [by_code[code](ctx)['usage'] for code in plain] == [1] * len(plain)
    # Parent-scoped endpoint checks require a cluster identifier in the inventory.
    assert [c[2](ctx)['usage'] for c in NEPTUNE[:3]] == [1, 1, 1]


def test_elasticache_nodes_are_counted_per_shard():
    """A replication group reports its shards as NodeGroups, and the quota is
    per shard rather than per group."""
    ctx = Mock()
    ctx.call.return_value = [
        {'ReplicationGroupId': 'group', 'NodeGroups': [
            {'NodeGroupId': '0001', 'NodeGroupMembers': [{}]},
            {'NodeGroupId': '0002', 'NodeGroupMembers': [{}, {}, {}]}]}]
    check = next(fn for code, _name, fn in CACHE if code == 'L-7D6587E6')
    result = check(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'group/0002')
