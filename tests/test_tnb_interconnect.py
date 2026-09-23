from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import interconnect, tnb
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys


NOW = datetime(2026, 9, 15, tzinfo=UTC)
UUID = '11111111-1111-1111-1111-11111111111'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 50}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


PACKAGE_FIELDS = {
    'list_sol_function_packages': {'onboardingState': 'ONBOARDED',
                                   'operationalState': 'ENABLED',
                                   'usageState': 'NOT_IN_USE'},
    'list_sol_network_packages': {'metadata': {'createdAt': NOW, 'lastModified': NOW},
                                  'nsdOnboardingState': 'ONBOARDED',
                                  'nsdOperationalState': 'ENABLED',
                                  'nsdUsageState': 'NOT_IN_USE'},
    'list_sol_network_instances': {'metadata': {'createdAt': NOW, 'lastModified': NOW},
                                   'nsInstanceDescription': 'demo',
                                   'nsInstanceName': 'demo', 'nsState': 'INSTANTIATED',
                                   'nsdId': 'nsd-1', 'nsdInfoId': 'nsdinfo-1'},
}


def package(method, identity):
    return dict(id=identity, arn=f'arn:aws:tnb:eu-central-1:123456789012:p/{identity}',
                **PACKAGE_FIELDS[method])


def operation(identity, state):
    return {'id': identity, 'arn': f'arn:aws:tnb:eu-central-1:123456789012:op/{identity}',
            'lcmOperationType': 'INSTANTIATE', 'nsInstanceId': 'ni-1',
            'operationState': state}


def test_packages_and_instances_are_counted_once():
    for code, method, key in (('L-08069DBD', 'list_sol_function_packages', 'functionPackages'),
                              ('L-3328748B', 'list_sol_network_packages', 'networkPackages'),
                              ('L-C92FB107', 'list_sol_network_instances', 'networkInstances')):
        ctx = context('tnb', code)
        with Stubber(ctx.client('tnb')) as stub:
            stub.add_response(method, {key: [package(method, 'a'), package(method, 'b'),
                                             package(method, 'a')]}, {})
            assert check(tnb, code)(ctx)['usage'] == 2, code
            stub.assert_no_pending_responses()


def test_only_processing_and_cancelling_operations_are_ongoing():
    ctx = context('tnb', 'L-81A3E723')
    with Stubber(ctx.client('tnb')) as stub:
        stub.add_response('list_sol_network_operations', {'networkOperations': [
            operation('o1', 'PROCESSING'), operation('o2', 'CANCELLING'),
            operation('o3', 'COMPLETED'), operation('o4', 'FAILED'),
            operation('o5', 'CANCELLED')]}, {})
        assert tnb.ongoing_operations(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_unknown_operation_state_raises_nodata():
    ctx = context('tnb', 'L-81A3E723')
    with Stubber(ctx.client('tnb')) as stub:
        stub.add_response('list_sol_network_operations', {'networkOperations': [
            operation('o1', 'PONDERING')]}, {})
        with pytest.raises(NoData, match='unknown state'):
            tnb.ongoing_operations(ctx)


def connection(identity, state='available', last_mile=None, cloud=None):
    # provider is a tagged union: a connection names one side, never both.
    provider = ({'lastMileProvider': last_mile} if last_mile is not None
                else {'cloudServiceProvider': cloud})
    return {'id': identity, 'state': state, 'provider': provider,
            'arn': f'arn:aws:interconnect:eu-central-1:123456789012:connection/{identity}',
            'description': identity, 'bandwidth': '1Gbps', 'environmentId': 'env-1',
            'attachPoint': {'directConnectGateway': f'{UUID}1'}, 'location': 'FRA',
            'type': 'standard', 'sharedId': f'{UUID}2'}


class FakeContext:
    """Return a fixed inventory, to reach validation the SDK shapes forbid."""

    def __init__(self, items):
        self.items = items

    def call(self, *args, **kwargs):
        return self.items


def test_created_connections_exclude_deleted_ones():
    ctx = context('interconnect', 'L-00139C4D')
    with Stubber(ctx.client('interconnect')) as stub:
        stub.add_response('list_connections', {'connections': [
            connection('c1', cloud='azure'), connection('c2', 'requested', cloud='gcp'),
            connection('c3', 'deleted', cloud='azure')]}, {})
        assert check(interconnect, 'L-00139C4D')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_outstanding_connections_count_requested_ones_only():
    ctx = context('interconnect', 'L-29F85628')
    with Stubber(ctx.client('interconnect')) as stub:
        stub.add_response('list_connections', {'connections': [
            connection('c1', cloud='azure'), connection('c2', 'requested', cloud='gcp'),
            connection('c3', 'pending', cloud='azure')]}, {})
        assert check(interconnect, 'L-29F85628')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_connections_are_grouped_by_each_side_of_the_provider_pair():
    connections = [connection('c1', last_mile='fiberco'),
                   connection('c2', last_mile='fiberco'),
                   connection('c3', last_mile='cableco'),
                   connection('c4', 'deleted', last_mile='fiberco'),
                   connection('c5', cloud='azure'), connection('c6', cloud='azure'),
                   connection('c7', cloud='gcp')]
    for code, expected_id in (('L-14D2B214', 'fiberco'), ('L-7B96960D', 'azure')):
        ctx = context('interconnect', code)
        with Stubber(ctx.client('interconnect')) as stub:
            stub.add_response('list_connections', {'connections': connections}, {})
            result = check(interconnect, code)(ctx)
            # The deleted connection is left out of both groupings.
            assert (result['usage'], result['resource_id']) == (2, expected_id), code
            stub.assert_no_pending_responses()


def test_a_connection_without_a_provider_raises_nodata():
    ctx = FakeContext([{'id': 'c1', 'state': 'available'}])
    with pytest.raises(NoData, match='no provider'):
        check(interconnect, 'L-14D2B214')(ctx)


def test_an_unknown_connection_state_raises_nodata():
    ctx = FakeContext([{'id': 'c1', 'state': 'melting'}])
    with pytest.raises(NoData, match='unknown state'):
        check(interconnect, 'L-00139C4D')(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((tnb, 'tnb'), (interconnect, 'interconnect')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
