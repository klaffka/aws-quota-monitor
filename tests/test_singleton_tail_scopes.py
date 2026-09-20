"""Four per-parent scopes, one each from the tail of the coverage sweep."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cloudtrail, docdb_elastic, elasticache, oam
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def sink_arn(name):
    return f'arn:aws:oam:{REGION}:{ACCOUNT}:sink/{name}'


def stub_sinks(stub, sinks):
    stub.add_response('list_sinks', {'Items': [
        {'Arn': sink_arn(name), 'Id': name, 'Name': name} for name in sinks]}, {})
    for name, links in sinks.items():
        stub.add_response('list_attached_links', {'Items': [
            {'Label': f'link{index}', 'LinkArn': f'arn:link/{index}'}
            for index in range(links)]}, {'SinkIdentifier': sink_arn(name)})


def test_the_sink_with_the_most_links_is_measured():
    ctx = context('oam', 'L-303A1B23')
    with Stubber(ctx.client('oam')) as stub:
        stub_sinks(stub, {'quiet': 1, 'busy': 4})
        result = check(oam, 'L-303A1B23')(ctx)
        assert (result['usage'], result['resource_id']) == (4, sink_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_sink_nothing_is_attached_to_counts_as_zero():
    ctx = context('oam', 'L-303A1B23')
    with Stubber(ctx.client('oam')) as stub:
        stub_sinks(stub, {'bare': 0})
        result = check(oam, 'L-303A1B23')(ctx)
        assert (result['usage'], result['resource_id']) == (0, sink_arn('bare'))
        stub.assert_no_pending_responses()


def stub_replication_groups(stub, groups):
    """``groups`` maps a group id to a list of member counts, one per shard."""
    stub.add_response('describe_replication_groups', {'ReplicationGroups': [
        {'ReplicationGroupId': identity, 'NodeGroups': [
            {'NodeGroupId': f'{index:04d}', 'NodeGroupMembers': [
                {'CacheClusterId': f'{identity}-{index}-{member}'}
                for member in range(members)]}
            for index, members in enumerate(shards)]}
        for identity, shards in groups.items()]}, {})


def test_the_shard_with_the_most_nodes_is_measured():
    """The quota is per shard, so the maximum runs over shards, not groups."""
    ctx = context('elasticache', 'L-7D6587E6')
    with Stubber(ctx.client('elasticache')) as stub:
        stub_replication_groups(stub, {'one': [2, 5], 'two': [3]})
        result = check(elasticache, 'L-7D6587E6')(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'one/0001')
        stub.assert_no_pending_responses()


def test_an_account_without_replication_groups_counts_as_zero():
    ctx = context('elasticache', 'L-7D6587E6')
    with Stubber(ctx.client('elasticache')) as stub:
        stub.add_response('describe_replication_groups', {'ReplicationGroups': []}, {})
        assert check(elasticache, 'L-7D6587E6')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def cluster_arn(name):
    return f'arn:aws:docdb-elastic:{REGION}:{ACCOUNT}:cluster/{name}'


def stub_clusters(stub, clusters):
    stub.add_response('list_clusters', {'clusters': [
        {'clusterArn': cluster_arn(name), 'clusterName': name, 'status': 'ACTIVE'}
        for name in clusters]}, {})
    for name, shards in clusters.items():
        stub.add_response('get_cluster', {'cluster': {
            'clusterArn': cluster_arn(name), 'clusterName': name, 'status': 'ACTIVE',
            'adminUserName': 'admin', 'authType': 'PLAIN_TEXT',
            'clusterEndpoint': f'{name}.docdb-elastic.test',
            'createTime': '2026-01-01T00:00:00Z', 'kmsKeyId': 'AWS_OWNED_KMS_KEY',
            'preferredMaintenanceWindow': 'sun:05:00-sun:06:00',
            'shardCapacity': 2, 'shardCount': shards,
            'subnetIds': ['subnet-1'], 'vpcSecurityGroupIds': ['sg-1']}},
            {'clusterArn': cluster_arn(name)})


def test_the_elastic_cluster_with_the_most_shards_is_measured():
    ctx = context('docdb-elastic', 'L-5CF76496')
    with Stubber(ctx.client('docdb-elastic')) as stub:
        stub_clusters(stub, {'quiet': 2, 'busy': 6})
        result = check(docdb_elastic, 'L-5CF76496')(ctx)
        assert (result['usage'], result['resource_id']) == (6, cluster_arn('busy'))
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for a response the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_cluster_stating_no_shard_count_is_reported():
    """The shard count is a required member, so only a broken response omits it."""
    ctx = FakeContext({'list_clusters': [{'clusterArn': cluster_arn('odd')}],
                       'get_cluster': {'cluster': {'clusterArn': cluster_arn('odd')}}})
    with pytest.raises(NoData, match='shard'):
        check(docdb_elastic, 'L-5CF76496')(ctx)


def stub_dashboards(stub, dashboards):
    stub.add_response('list_dashboards', {'Dashboards': [
        {'DashboardArn': f'arn:dashboard/{name}', 'Type': 'CUSTOM'}
        for name in dashboards]}, {})
    for name, widgets in dashboards.items():
        stub.add_response('get_dashboard', {
            'DashboardArn': f'arn:dashboard/{name}', 'Type': 'CUSTOM',
            'Status': 'CREATED',
            'Widgets': [{'QueryStatement': f'select {index}'}
                        for index in range(widgets)]},
            {'DashboardId': f'arn:dashboard/{name}'})


def test_the_dashboard_with_the_most_widgets_is_measured():
    ctx = context('cloudtrail', 'L-84EB1525')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub_dashboards(stub, {'quiet': 1, 'busy': 3})
        result = check(cloudtrail, 'L-84EB1525')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'arn:dashboard/busy')
        stub.assert_no_pending_responses()


def test_a_dashboard_without_widgets_counts_as_zero():
    ctx = context('cloudtrail', 'L-84EB1525')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub_dashboards(stub, {'bare': 0})
        result = check(cloudtrail, 'L-84EB1525')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'arn:dashboard/bare')
        stub.assert_no_pending_responses()
