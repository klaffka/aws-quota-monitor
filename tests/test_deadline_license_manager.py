from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import deadline, license_manager
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

FARM = 'farm-11111111111111111111111111111111'
FLEET = 'fleet-11111111111111111111111111111111'
QUEUE = 'queue-11111111111111111111111111111111'
OTHER_QUEUE = 'queue-22222222222222222222222222222222'
LICENSE = 'arn:aws:license-manager::123456789012:license:l-1111'
OTHER_LICENSE = 'arn:aws:license-manager::123456789012:license:l-2222'
NOW = datetime(2026, 9, 15, tzinfo=UTC)
STAMP = {'createdAt': NOW, 'createdBy': 'arn:aws:iam::123456789012:user/build'}
FLEET_TWO = 'fleet-22222222222222222222222222222222'


def farm(identity=FARM, name='main'):
    return dict(farmId=identity, displayName=name, **STAMP)


def fleet(identity, name='render'):
    return dict(fleetId=identity, farmId=FARM, displayName=name, status='ACTIVE',
                workerCount=1, minWorkerCount=0, maxWorkerCount=10,
                configuration={'customerManaged': {
                    'mode': 'NO_SCALING',
                    'workerCapabilities': {'vCpuCount': {'min': 1},
                                           'memoryMiB': {'min': 1024},
                                           'osFamily': 'LINUX',
                                           'cpuArchitectureType': 'x86_64'}}},
                **STAMP)


def queue(identity):
    return dict(farmId=FARM, queueId=identity, displayName=identity, status='IDLE',
                defaultBudgetAction='NONE', **STAMP)


def worker(identity, fleet_id):
    return dict(farmId=FARM, fleetId=fleet_id, workerId=identity,
                status='CREATED', **STAMP)


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_workers_are_summed_across_a_farms_fleets():
    ctx = context('deadline', 'L-48CC9B8E')
    with Stubber(ctx.client('deadline')) as stub:
        stub.add_response('list_farms', {'farms': [farm()]}, {})
        stub.add_response('list_fleets', {'fleets': [
            fleet(FLEET), fleet(FLEET_TWO, 'sim')]}, {'farmId': FARM})
        stub.add_response('list_workers', {'workers': [
            worker('worker-1', FLEET)]}, {'farmId': FARM, 'fleetId': FLEET})
        stub.add_response('list_workers', {'workers': [
            worker('worker-2', FLEET_TWO), worker('worker-3', FLEET_TWO)]},
            {'farmId': FARM, 'fleetId': FLEET_TWO})
        result = check(deadline, 'L-48CC9B8E')(ctx)
        # ListWorkers takes a fleet, so the farm total sums its fleets.
        assert (result['usage'], result['resource_id']) == (3, FARM)
        stub.assert_no_pending_responses()


def test_queue_limit_associations_are_reported_per_queue():
    ctx = context('deadline', 'L-55B7030C')
    with Stubber(ctx.client('deadline')) as stub:
        stub.add_response('list_farms', {'farms': [farm()]}, {})
        stub.add_response('list_queues', {'queues': [
            queue(QUEUE), queue(OTHER_QUEUE)]}, {'farmId': FARM})
        stub.add_response('list_queue_limit_associations', {
            'queueLimitAssociations': [
                dict(queueId=QUEUE, limitId='limit-1', status='ACTIVE', **STAMP),
                dict(queueId=QUEUE, limitId='limit-2', status='ACTIVE', **STAMP)]},
            {'farmId': FARM})
        result = deadline.queue_limit_associations_per_queue(ctx)
        assert (result['usage'], result['resource_id']) == (2, f'{FARM}/{QUEUE}')
        stub.assert_no_pending_responses()


def test_a_farm_without_an_identity_raises_nodata():
    ctx = context('deadline', 'L-2DEF7E07')
    with Stubber(ctx.client('deadline')) as stub:
        # The SDK requires a farm id in the response, so this drives the helper.
        stub.add_response('list_farms', {'farms': []}, {})
        assert deadline.farms(ctx) == []
    with pytest.raises(NoData, match='missing its identity'):
        deadline._identity({'displayName': 'nameless'}, 'farmId', 'farm')


def license_entry(arn, units):
    return {'LicenseArn': arn, 'LicenseName': arn, 'ProductName': 'Studio',
            'Status': 'AVAILABLE',
            'Entitlements': [{'Name': f'e{index}', 'Unit': unit}
                             for index, unit in enumerate(units)]}


def test_entitlements_split_counted_units_from_the_rest():
    entries = [license_entry(LICENSE, ['Count', 'Count', 'Gigabytes']),
               license_entry(OTHER_LICENSE, ['Bytes', 'Gigabytes', 'Megabytes'])]
    for code, expected_usage, expected_id in (('L-D92A2CE4', 2, LICENSE),
                                              ('L-CA3CD2C4', 3, OTHER_LICENSE)):
        ctx = context('license-manager', code)
        with Stubber(ctx.client('license-manager')) as stub:
            stub.add_response('list_licenses', {'Licenses': entries}, {})
            result = check(license_manager, code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def grant(identity, license_arn):
    return {'GrantArn': f'arn:aws:license-manager::123456789012:grant:{identity}',
            'GrantName': identity, 'ParentArn': license_arn,
            'LicenseArn': license_arn,
            'GranteePrincipalArn': 'arn:aws:iam::222222222222:root',
            'HomeRegion': 'eu-central-1', 'GrantStatus': 'ACTIVE', 'Version': '1',
            'GrantedOperations': ['CheckoutLicense']}


def token(identity, license_arn):
    return {'TokenId': identity, 'TokenType': 'REFRESH_TOKEN',
            'LicenseArn': license_arn, 'Status': 'AVAILABLE'}


def test_grants_and_tokens_are_counted_per_license():
    for code, method, key, builder in (
            ('L-55F04DE6', 'list_distributed_grants', 'Grants', grant),
            ('L-992B7443', 'list_tokens', 'Tokens', token)):
        ctx = context('license-manager', code)
        with Stubber(ctx.client('license-manager')) as stub:
            stub.add_response('list_licenses', {'Licenses': [
                license_entry(LICENSE, ['Count']),
                license_entry(OTHER_LICENSE, ['Count'])]}, {})
            stub.add_response(method, {key: [
                builder('a', LICENSE), builder('b', LICENSE),
                builder('c', OTHER_LICENSE)]}, {})
            result = check(license_manager, code)(ctx)
            assert (result['usage'], result['resource_id']) == (2, LICENSE), code
            stub.assert_no_pending_responses()


def test_configuration_associations_are_inverted_onto_the_resource():
    ctx = context('license-manager', 'L-0B08C8C5')
    configuration = 'arn:aws:license-manager:eu-central-1:123456789012:license-configuration:lic-1'
    resource = 'arn:aws:ec2:eu-central-1:123456789012:instance/i-1'
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_configurations', {'LicenseConfigurations': [
            {'LicenseConfigurationArn': configuration, 'Name': 'lic'}]}, {})
        stub.add_response('list_associations_for_license_configuration', {
            'LicenseConfigurationAssociations': [
                {'ResourceArn': resource, 'ResourceType': 'EC2_INSTANCE'}]},
            {'LicenseConfigurationArn': configuration})
        result = license_manager.associations_per_resource(ctx)
        assert (result['usage'], result['resource_id']) == (1, resource)
        stub.assert_no_pending_responses()


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((deadline, 'deadline'),
                            (license_manager, 'license-manager')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
