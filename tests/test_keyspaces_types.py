import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cassandra
from modules.qmcore.aws import CheckContext, NoData


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cassandra', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in cassandra.CHECKS if candidate == code)


def keyspace(stub, name='shop'):
    stub.add_response('list_keyspaces', {'keyspaces': [
        {'keyspaceName': name, 'replicationStrategy': 'SINGLE_REGION',
         'resourceArn': f'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/{name}/'}]},
        {})


def udt(stub, keyspace_name, name, tables=(), parents=()):
    stub.add_response('get_type', {
        'keyspaceName': keyspace_name, 'typeName': name,
        'directReferringTables': list(tables), 'directParentTypes': list(parents),
        'maxNestingDepth': 1,
        'keyspaceArn': f'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/{keyspace_name}/'},
        {'keyspaceName': keyspace_name, 'typeName': name})


def test_types_are_measured_in_both_directions():
    ctx = context('L-7A88D508')
    with Stubber(ctx.client('keyspaces')) as stub:
        keyspace(stub)
        stub.add_response('list_types', {'types': ['address', 'contact']},
                          {'keyspaceName': 'shop'})
        udt(stub, 'shop', 'address', tables=['orders', 'customers'])
        udt(stub, 'shop', 'contact', tables=['customers'], parents=['address'])
        assert check('L-7A88D508')(ctx)['usage'] == 2
        tables = check('L-089904FB')(ctx)
        assert (tables['usage'], tables['resource_id']) == (2, 'shop.address')
        per_table = check('L-96FEFC6D')(ctx)
        assert (per_table['usage'], per_table['resource_id']) == (2, 'shop.customers')
        parents = check('L-C63C913D')(ctx)
        assert (parents['usage'], parents['resource_id']) == (1, 'shop.contact')
        children = check('L-F90953AC')(ctx)
        assert (children['usage'], children['resource_id']) == (1, 'shop.address')
        longest = check('L-964C49BD')(ctx)
        assert (longest['usage'], longest['resource_id']) == (7, 'shop.address')
        stub.assert_no_pending_responses()


def test_a_type_that_answers_for_another_identity_raises_nodata():
    ctx = context('L-7A88D508')
    with Stubber(ctx.client('keyspaces')) as stub:
        keyspace(stub)
        stub.add_response('list_types', {'types': ['address']},
                          {'keyspaceName': 'shop'})
        # The answer names a different type than the request asked for.
        stub.add_response('get_type', {
            'keyspaceName': 'shop', 'typeName': 'contact',
            'directReferringTables': [], 'directParentTypes': [],
            'maxNestingDepth': 1,
            'keyspaceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/shop/'},
            {'keyspaceName': 'shop', 'typeName': 'address'})
        with pytest.raises(NoData, match='does not match the requested identity'):
            check('L-7A88D508')(ctx)


def test_tables_are_listed_for_every_keyspace():
    ctx = context('L-BF48748A')
    with Stubber(ctx.client('keyspaces')) as stub:
        stub.add_response('list_keyspaces', {'keyspaces': [
            {'keyspaceName': 'shop', 'replicationStrategy': 'SINGLE_REGION',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/shop/'},
            {'keyspaceName': 'logs', 'replicationStrategy': 'SINGLE_REGION',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/logs/'}]},
            {})
        stub.add_response('list_tables', {'tables': [
            {'keyspaceName': 'shop', 'tableName': 'orders',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/shop/table/orders'}]},
            {'keyspaceName': 'shop'})
        stub.add_response('list_tables', {'tables': [
            {'keyspaceName': 'logs', 'tableName': 'events',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/logs/table/events'},
            {'keyspaceName': 'logs', 'tableName': 'audit',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/logs/table/audit'}]},
            {'keyspaceName': 'logs'})
        assert check('L-BF48748A')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


SYSTEM_KEYSPACES = ('system', 'system_schema', 'system_schema_mcs', 'system_multiregion_info')


def test_system_keyspaces_are_not_the_accounts_own():
    """ListKeyspaces returns AWS's system keyspaces once the role may read them;
    they count towards no quota, and GetTable on them fails."""
    ctx = context('L-677FFD22')
    with Stubber(ctx.client('keyspaces')) as stub:
        stub.add_response('list_keyspaces', {'keyspaces': [
            {'keyspaceName': name, 'replicationStrategy': 'SINGLE_REGION',
             'resourceArn': f'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/{name}/'}
            for name in (*SYSTEM_KEYSPACES, 'shop')]}, {})
        stub.add_response('list_tables', {'tables': [
            {'keyspaceName': 'shop', 'tableName': 'orders',
             'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/shop/table/orders'}]},
            {'keyspaceName': 'shop'})
        stub.add_response('get_table', {
            'keyspaceName': 'shop', 'tableName': 'orders',
            'resourceArn': 'arn:aws:cassandra:eu-central-1:123456789012:/keyspace/shop/table/orders',
            'capacitySpecification': {'throughputMode': 'PROVISIONED',
                                      'readCapacityUnits': 40, 'writeCapacityUnits': 10}},
            {'keyspaceName': 'shop', 'tableName': 'orders'})
        assert check('L-677FFD22')(ctx)['usage'] == 1
        assert check('L-17766544')(ctx)['usage'] == 40
        stub.assert_no_pending_responses()
