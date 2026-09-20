"""ElastiCache regional subnet-group inventory and shard node scopes."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def count(method, key):
    return lambda ctx: dict(usage=len(ctx.call('elasticache', method, key)),
                            source=f'elasticache:{method}', method='ACCOUNT_COUNT')


def nodes_per_shard(ctx):
    """The quota is per shard, so the maximum runs over shards, not groups."""
    values = []
    for group in ctx.call('elasticache', 'describe_replication_groups',
                          'ReplicationGroups'):
        identity = group.get('ReplicationGroupId')
        if not isinstance(identity, str) or not identity:
            raise NoData('ElastiCache replication group is missing its identity')
        for shard in group.get('NodeGroups') or ():
            shard_id = shard.get('NodeGroupId')
            if not isinstance(shard_id, str) or not shard_id:
                raise NoData('ElastiCache shard is missing its identity')
            members = shard.get('NodeGroupMembers') or []
            values.append((f'{identity}/{shard_id}', len(members), None))
    return maximum(values, 'ElastiCacheShard', 'elasticache:DescribeReplicationGroups')


CHECKS = [
    ('L-3E7F7726', 'Subnet groups per Region', count('describe_cache_subnet_groups', 'CacheSubnetGroups')),
    ('L-80E085C7', 'Users per Region', count('describe_users', 'Users')),
    ('L-3F15A733', 'Parameter groups per Region', count('describe_cache_parameter_groups', 'CacheParameterGroups')),
    ('L-AD484FC5', 'User Groups per Region', count('describe_user_groups', 'UserGroups')),
    ('L-BBCDAECC', 'Serverless Caches per Region', count('describe_serverless_caches', 'ServerlessCaches')),
    ('L-7D6587E6', 'Nodes per shard', nodes_per_shard),
]


def get_current_quotastatus_elasticache(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'elasticache' for service, _ in context.quotas): return []
    return context.run('elasticache', CHECKS, skip)
