"""Provisioned capacity: a stored setting, not the rate a table actually serves."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cassandra, dynamodb
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def stub_tables(stub, tables):
    """``tables`` maps a table name to ``(read units, write units)`` or None."""
    stub.add_response('list_tables', {'TableNames': list(tables)}, {})
    for name, capacity in tables.items():
        table = {'TableName': name}
        if capacity is not None:
            read, write = capacity
            table['ProvisionedThroughput'] = {'ReadCapacityUnits': read,
                                              'WriteCapacityUnits': write}
        stub.add_response('describe_table', {'Table': table}, {'TableName': name})


def test_the_table_with_the_most_provisioned_reads_is_measured():
    ctx = context('dynamodb', 'L-CF0CBE56')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'quiet': (5, 5), 'busy': (4000, 10)})
        result = check(dynamodb, 'L-CF0CBE56')(ctx)
        assert (result['usage'], result['resource_id']) == (4000, 'busy')
        stub.assert_no_pending_responses()


def test_the_write_scope_reads_the_other_half_of_the_same_setting():
    ctx = context('dynamodb', 'L-AB614373')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'quiet': (5, 5), 'busy': (4000, 10)})
        result = check(dynamodb, 'L-AB614373')(ctx)
        assert (result['usage'], result['resource_id']) == (10, 'busy')
        stub.assert_no_pending_responses()


def test_an_on_demand_table_provisions_nothing():
    """A table billed per request states no provisioned throughput at all."""
    ctx = context('dynamodb', 'L-CF0CBE56')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'ondemand': None})
        result = check(dynamodb, 'L-CF0CBE56')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'ondemand')
        stub.assert_no_pending_responses()


def test_the_throughput_scopes_share_the_describe_the_index_count_makes():
    """All three DynamoDB table scopes read one describe per table."""
    ctx = context('dynamodb', 'L-F7858A77')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub.add_response('list_tables', {'TableNames': ['one']}, {})
        stub.add_response('describe_table', {'Table': {
            'TableName': 'one',
            'GlobalSecondaryIndexes': [{'IndexName': 'gsi'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 25,
                                      'WriteCapacityUnits': 7}}},
            {'TableName': 'one'})
        assert check(dynamodb, 'L-F7858A77')(ctx)['usage'] == 1
        assert check(dynamodb, 'L-CF0CBE56')(ctx)['usage'] == 25
        assert check(dynamodb, 'L-AB614373')(ctx)['usage'] == 7
        stub.assert_no_pending_responses()


def stub_keyspaces(stub, tables):
    """``tables`` maps a table name to ``(read units, write units)`` or None."""
    keyspace_arn = f'arn:aws:cassandra:{REGION}:{ACCOUNT}:/keyspace/space/'
    stub.add_response('list_keyspaces', {'keyspaces': [
        {'keyspaceName': 'space', 'resourceArn': keyspace_arn,
         'replicationStrategy': 'SINGLE_REGION'}]}, {})
    stub.add_response('list_tables', {'tables': [
        {'tableName': name, 'keyspaceName': 'space',
         'resourceArn': f'{keyspace_arn}table/{name}'} for name in tables]},
        {'keyspaceName': 'space'})
    for name, capacity in tables.items():
        table = {'keyspaceName': 'space', 'tableName': name,
                 'resourceArn': f'{keyspace_arn}table/{name}'}
        if capacity is None:
            table['capacitySpecification'] = {'throughputMode': 'PAY_PER_REQUEST'}
        else:
            read, write = capacity
            table['capacitySpecification'] = {'throughputMode': 'PROVISIONED',
                                              'readCapacityUnits': read,
                                              'writeCapacityUnits': write}
        stub.add_response('get_table', table,
                          {'keyspaceName': 'space', 'tableName': name})


def test_the_keyspaces_table_with_the_most_provisioned_reads_is_measured():
    ctx = context('cassandra', 'L-17766544')
    with Stubber(ctx.client('keyspaces')) as stub:
        stub_keyspaces(stub, {'quiet': (10, 10), 'busy': (900, 40)})
        result = check(cassandra, 'L-17766544')(ctx)
        assert (result['usage'], result['resource_id']) == (900, 'space.busy')
        stub.assert_no_pending_responses()


def test_the_keyspaces_write_scope_reads_the_other_half():
    ctx = context('cassandra', 'L-3D8ED127')
    with Stubber(ctx.client('keyspaces')) as stub:
        stub_keyspaces(stub, {'quiet': (10, 10), 'busy': (900, 40)})
        result = check(cassandra, 'L-3D8ED127')(ctx)
        assert (result['usage'], result['resource_id']) == (40, 'space.busy')
        stub.assert_no_pending_responses()


def test_a_pay_per_request_keyspaces_table_provisions_nothing():
    ctx = context('cassandra', 'L-17766544')
    with Stubber(ctx.client('keyspaces')) as stub:
        stub_keyspaces(stub, {'ondemand': None})
        result = check(cassandra, 'L-17766544')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'space.ondemand')
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for a response the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_keyspaces_table_detail_that_names_another_table_is_reported():
    """The detail is asked for by name, so a different one is not trusted."""
    ctx = FakeContext({'list_keyspaces': [{'keyspaceName': 'space'}],
                       'list_tables': [{'tableName': 'one'}],
                       'get_table': {'keyspaceName': 'space', 'tableName': 'other'}})
    with pytest.raises(NoData, match='match'):
        check(cassandra, 'L-17766544')(ctx)
