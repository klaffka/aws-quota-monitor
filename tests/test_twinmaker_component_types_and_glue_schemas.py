"""TwinMaker component type scopes and Glue schema version inventories."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import glue, twinmaker
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)
ARN = 'arn:aws:glue:eu-central-1:123456789012:schema/registry/one'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


# GetComponentType validates every flag a property definition carries.
PROPERTY = {'dataType': {'type': 'STRING'}, 'isTimeSeries': False,
            'isRequiredInEntity': False, 'isExternalId': False,
            'isStoredExternally': False, 'isImported': False, 'isFinal': False,
            'isInherited': False}


def workspace(identity):
    return {'workspaceId': identity, 'arn': f'arn:aws:iottwinmaker:eu-central-1:123456789012:workspace/{identity}',
            'creationDateTime': MOMENT, 'updateDateTime': MOMENT}


def component_type(identity):
    return {'componentTypeId': identity, 'arn': f'arn:aws:iottwinmaker:eu-central-1:123456789012:workspace/ws-1/componenttype/{identity}',
            'creationDateTime': MOMENT, 'updateDateTime': MOMENT,
            'status': {'state': 'ACTIVE'}}


def component_type_detail(workspace_id, identity, properties=(), extends=()):
    return {'workspaceId': workspace_id, 'componentTypeId': identity,
            'arn': f'arn:aws:iottwinmaker:eu-central-1:123456789012:workspace/ws-1/componenttype/{identity}', 'creationDateTime': MOMENT,
            'updateDateTime': MOMENT, 'isAbstract': False, 'isSchemaInitialized': True,
            'propertyDefinitions': {name: PROPERTY for name in properties},
            'extendsFrom': list(extends)}


@pytest.mark.parametrize('code, expected, resource', [
    ('L-D8DF6F6C', 3, 'ws-1/rich'),     # properties per component type
    ('L-0169BFDB', 2, 'ws-1/derived'),  # parent component types per child
])
def test_component_type_scopes_take_the_largest_across_workspaces(code, expected, resource):
    ctx = context('iottwinmaker', code)
    with Stubber(ctx.client('iottwinmaker')) as stub:
        stub.add_response('list_workspaces', {'workspaceSummaries': [workspace('ws-1')]}, {})
        stub.add_response('list_component_types', {
            'workspaceId': 'ws-1',
            'componentTypeSummaries': [component_type('rich'), component_type('derived')]},
            {'workspaceId': 'ws-1'})
        stub.add_response('get_component_type',
                          component_type_detail('ws-1', 'rich', properties=('a', 'b', 'c')),
                          {'workspaceId': 'ws-1', 'componentTypeId': 'rich'})
        stub.add_response('get_component_type',
                          component_type_detail('ws-1', 'derived', properties=('a',),
                                                extends=('base-one', 'base-two')),
                          {'workspaceId': 'ws-1', 'componentTypeId': 'derived'})
        result = check(code, twinmaker.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, resource)
        stub.assert_no_pending_responses()


def test_a_component_type_detail_for_a_different_type_is_reported():
    ctx = context('iottwinmaker', 'L-D8DF6F6C')
    with Stubber(ctx.client('iottwinmaker')) as stub:
        stub.add_response('list_workspaces', {'workspaceSummaries': [workspace('ws-1')]}, {})
        stub.add_response('list_component_types', {
            'workspaceId': 'ws-1', 'componentTypeSummaries': [component_type('rich')]},
            {'workspaceId': 'ws-1'})
        stub.add_response('get_component_type', component_type_detail('ws-1', 'other'),
                          {'workspaceId': 'ws-1', 'componentTypeId': 'rich'})
        with pytest.raises(NoData, match='identity'):
            check('L-D8DF6F6C', twinmaker.CHECKS)(ctx)


def schema(name):
    return {'RegistryName': 'registry', 'SchemaName': name,
            'SchemaArn': f'{ARN}-{name}', 'SchemaStatus': 'AVAILABLE',
            'CreatedTime': '2026-09-16', 'UpdatedTime': '2026-09-16'}


def version(schema_name, version_id, number):
    return {'SchemaArn': f'{ARN}-{schema_name}', 'SchemaVersionId': version_id,
            'VersionNumber': number, 'Status': 'AVAILABLE', 'CreatedTime': '2026-09-16'}


def test_schema_versions_are_counted_per_schema():
    ctx = context('glue', 'L-AD871090')
    with Stubber(ctx.client('glue')) as stub:
        stub.add_response('list_schemas', {'Schemas': [schema('one'), schema('two')]}, {})
        stub.add_response('list_schema_versions', {'Schemas': [
            version('one', '11111111-1111-1111-1111-111111111111', 1)]},
            {'SchemaId': {'SchemaArn': f'{ARN}-one'}})
        stub.add_response('list_schema_versions', {'Schemas': [
            version('two', '22222222-2222-2222-2222-222222222222', 1),
            version('two', '33333333-3333-3333-3333-333333333333', 2)]},
            {'SchemaId': {'SchemaArn': f'{ARN}-two'}})
        result = check('L-AD871090', glue.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, f'{ARN}-two')
        stub.assert_no_pending_responses()


def test_metadata_pairs_are_counted_per_schema_version():
    ctx = context('glue', 'L-CB69DFA0')
    identity = '11111111-1111-1111-1111-111111111111'
    with Stubber(ctx.client('glue')) as stub:
        stub.add_response('list_schemas', {'Schemas': [schema('one')]}, {})
        stub.add_response('list_schema_versions', {'Schemas': [version('one', identity, 1)]},
                          {'SchemaId': {'SchemaArn': f'{ARN}-one'}})
        stub.add_response('query_schema_version_metadata', {
            'SchemaVersionId': identity,
            'MetadataInfoMap': {'owner': {'MetadataValue': 'team'},
                                'tier': {'MetadataValue': 'gold'}}},
            {'SchemaVersionId': identity})
        result = check('L-CB69DFA0', glue.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, identity)
        stub.assert_no_pending_responses()
