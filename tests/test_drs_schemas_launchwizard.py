from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import drs, launchwizard, schemas
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)
SERVER = 's-00000000000000001'
OTHER = 's-00000000000000002'
JOB = 'drsjob-00000000000000001'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def server(identity=SERVER, state='CONTINUOUS'):
    result = {'sourceServerID': identity}
    if state is not None:
        result['dataReplicationInfo'] = {'dataReplicationState': state}
    return result


def job(identity=JOB, status='STARTED', participants=(SERVER,)):
    return {'jobID': identity, 'status': status,
            'participatingServers': [{'sourceServerID': item} for item in participants]}


def test_replicating_servers_exclude_only_stopped_and_disconnected():
    ctx = context('drs', 'L-C1D14A2B')
    with Stubber(ctx.client('drs')) as stub:
        stub.add_response('describe_source_servers', {'items': [
            server(SERVER, 'CONTINUOUS'), server('s-00000000000000003', 'PAUSED'),
            server('s-00000000000000004', 'STOPPED'),
            server('s-00000000000000005', 'DISCONNECTED'),
            server('s-00000000000000006', None)]}, {})
        assert drs.replicating_source_servers(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_unknown_replication_state_raises_nodata():
    ctx = context('drs', 'L-C1D14A2B')
    with Stubber(ctx.client('drs')) as stub:
        stub.add_response('describe_source_servers', {'items': [
            {'sourceServerID': SERVER,
             'dataReplicationInfo': {'dataReplicationState': 'WARP_SPEED'}}]}, {})
        with pytest.raises(NoData, match='unknown replication state'):
            drs.replicating_source_servers(ctx)


def test_job_counts_ignore_completed_jobs():
    ctx = context('drs', 'L-D88FAC3A')
    with Stubber(ctx.client('drs')) as stub:
        stub.add_response('describe_jobs', {'items': [
            job(), job('drsjob-00000000000000002', 'PENDING'),
            job('drsjob-00000000000000003', 'COMPLETED')]}, {})
        assert check(drs, 'L-D88FAC3A')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_servers_in_jobs_are_reported_per_job_and_in_total():
    for code, expected in (('L-B827C881', 2), ('L-05AFA8C6', 3)):
        ctx = context('drs', code)
        with Stubber(ctx.client('drs')) as stub:
            stub.add_response('describe_jobs', {'items': [
                job(JOB, 'STARTED', (SERVER, OTHER)),
                job('drsjob-00000000000000002', 'PENDING', (SERVER,)),
                job('drsjob-00000000000000003', 'COMPLETED', (SERVER, OTHER))]}, {})
            assert check(drs, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_jobs_per_source_server_include_servers_without_jobs():
    ctx = context('drs', 'L-DD6D028C')
    with Stubber(ctx.client('drs')) as stub:
        stub.add_response('describe_source_servers', {'items': [
            server(SERVER), server(OTHER)]}, {})
        stub.add_response('describe_jobs', {'items': [
            job(JOB, 'STARTED', (SERVER,)),
            job('drsjob-00000000000000002', 'STARTED', (SERVER,))]}, {})
        result = drs.jobs_per_source_server(ctx)
        assert (result['usage'], result['resource_id']) == (2, SERVER)
        stub.assert_no_pending_responses()


def test_launch_actions_are_counted_per_source_server():
    ctx = context('drs', 'L-0588D03B')
    with Stubber(ctx.client('drs')) as stub:
        stub.add_response('describe_source_servers', {'items': [
            server(SERVER), server(OTHER)]}, {})
        stub.add_response('list_launch_actions', {'items': [
            {'actionId': 'a1'}, {'actionId': 'a2'}]}, {'resourceId': SERVER})
        stub.add_response('list_launch_actions', {'items': []}, {'resourceId': OTHER})
        result = drs.launch_actions_per_resource(ctx)
        assert (result['usage'], result['resource_id']) == (2, SERVER)
        stub.assert_no_pending_responses()


def registry(name):
    return {'RegistryName': name,
            'RegistryArn': f'arn:aws:schemas:eu-central-1:123456789012:registry/{name}'}


def schema(name, versions=1):
    return {'SchemaName': name, 'VersionCount': versions, 'LastModified': NOW,
            'SchemaArn': f'arn:aws:schemas:eu-central-1:123456789012:schema/{name}'}


def test_schemas_are_counted_per_registry():
    ctx = context('schemas', 'L-EE9E5FA9')
    with Stubber(ctx.client('schemas')) as stub:
        stub.add_response('list_registries', {'Registries': [
            registry('orders'), registry('billing')]}, {})
        stub.add_response('list_schemas', {'Schemas': [schema('one')]},
                          {'RegistryName': 'orders'})
        stub.add_response('list_schemas', {'Schemas': [schema('a'), schema('b')]},
                          {'RegistryName': 'billing'})
        result = check(schemas, 'L-EE9E5FA9')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'billing')
        stub.assert_no_pending_responses()


def test_schema_versions_use_the_reported_counter():
    ctx = context('schemas', 'L-3C443A2A')
    with Stubber(ctx.client('schemas')) as stub:
        stub.add_response('list_registries', {'Registries': [registry('orders')]}, {})
        stub.add_response('list_schemas', {'Schemas': [
            schema('one', 3), schema('two', 7)]}, {'RegistryName': 'orders'})
        result = schemas.versions_per_schema(ctx)
        assert (result['usage'], result['resource_id']) == (7, 'orders/two')
        stub.assert_no_pending_responses()


def test_discovered_schemas_are_zero_without_the_discovery_registry():
    ctx = context('schemas', 'L-1738102F')
    with Stubber(ctx.client('schemas')) as stub:
        stub.add_response('list_registries', {'Registries': [registry('orders')]}, {})
        assert schemas.discovered_schemas(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_discovered_schemas_count_that_registry_only():
    ctx = context('schemas', 'L-1738102F')
    with Stubber(ctx.client('schemas')) as stub:
        stub.add_response('list_registries', {'Registries': [
            registry('orders'), registry(schemas.DISCOVERED_REGISTRY)]}, {})
        stub.add_response('list_schemas', {'Schemas': [schema('a'), schema('b')]},
                          {'RegistryName': schemas.DISCOVERED_REGISTRY})
        assert schemas.discovered_schemas(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def deployment(identity, status):
    return {'id': identity, 'status': status, 'name': identity}


def test_deployment_counts_separate_deleted_failed_and_in_progress():
    states = [deployment('d1', 'COMPLETED'), deployment('d2', 'IN_PROGRESS'),
              deployment('d3', 'FAILED'), deployment('d4', 'DELETED'),
              deployment('d5', 'CREATING')]
    for code, expected in (('L-067B0AC5', 4), ('L-E64920AC', 3), ('L-0DE2E185', 2)):
        ctx = context('launchwizard', code)
        with Stubber(ctx.client('launch-wizard')) as stub:
            stub.add_response('list_deployments', {'deployments': states}, {})
            assert check(launchwizard, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_an_unknown_deployment_status_raises_nodata():
    ctx = context('launchwizard', 'L-067B0AC5')
    with Stubber(ctx.client('launch-wizard')) as stub:
        stub.add_response('list_deployments', {'deployments': [
            {'id': 'd1', 'status': 'PONDERING'}]}, {})
        with pytest.raises(NoData, match='unknown status'):
            check(launchwizard, 'L-067B0AC5')(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((drs, 'drs'), (schemas, 'schemas'),
                            (launchwizard, 'launchwizard')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
