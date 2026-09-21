"""Amazon DocumentDB elastic cluster counts and shard scopes."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def shards_per_cluster(ctx):
    """The listing carries no shard count, so each cluster is fetched."""
    values = []
    for summary in ctx.call('docdb-elastic', 'list_clusters', 'clusters'):
        arn = summary.get('clusterArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('DocumentDB elastic cluster is missing its ARN')
        cluster = ctx.call('docdb-elastic', 'get_cluster',
                           clusterArn=arn).get('cluster') or {}
        shards = cluster.get('shardCount')
        if not isinstance(shards, int):
            raise NoData('DocumentDB elastic cluster states no shard count')
        values.append((arn, shards, None))
    return maximum(values, 'DocumentDBElasticCluster', 'docdb-elastic:GetCluster')

CHECKS = [('L-B3699347', 'Elastic clusters',
           lambda c: dict(usage=len(c.call('docdb-elastic', 'list_clusters', 'clusters')),
                          source='docdb-elastic:ListClusters', method='ACCOUNT_COUNT')),
          ('L-5CF76496', 'Shards per elastic cluster', shards_per_cluster)]


def get_current_quotastatus_docdb_elastic(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'docdb-elastic' for service, _ in context.quotas): return []
    return context.run('docdb-elastic', CHECKS, skip)
