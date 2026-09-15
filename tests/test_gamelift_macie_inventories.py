"""GameLift fleet-scoped and Macie job-scoped inventories."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import gamelift, macie
from modules.qmcore.aws import CheckContext

FLEETS = [{'FleetId': 'fleet-ec2', 'ComputeType': 'EC2'},
          {'FleetId': 'fleet-any', 'ComputeType': 'ANYWHERE'},
          {'FleetId': 'fleet-any-2', 'ComputeType': 'ANYWHERE'}]


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


@pytest.mark.parametrize('code, expected', [('L-FDDD1260', 1), ('L-593688D9', 2)])
def test_fleets_are_counted_by_compute_type(code, expected):
    """ListFleets mixes the types; each quota counts only its own."""
    ctx = context('gamelift', code)
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes', {'FleetAttributes': FLEETS}, {})
        assert check(gamelift, code)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def test_compute_is_counted_only_for_anywhere_fleets():
    ctx = context('gamelift', 'L-0536A98D')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes', {'FleetAttributes': FLEETS}, {})
        stub.add_response('list_compute', {'ComputeList': [{'ComputeName': 'one'}]},
                          {'FleetId': 'fleet-any'})
        stub.add_response('list_compute', {'ComputeList': [{'ComputeName': 'two'},
                                                           {'ComputeName': 'three'}]},
                          {'FleetId': 'fleet-any-2'})
        result = check(gamelift, 'L-0536A98D')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'fleet-any-2')
        stub.assert_no_pending_responses()


def test_queue_destinations_use_the_largest_queue():
    ctx = context('gamelift', 'L-BB62CF1D')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_game_session_queues', {'GameSessionQueues': [
            {'Name': 'small', 'Destinations': [{'DestinationArn': 'arn:one'}]},
            {'Name': 'large', 'Destinations': [{'DestinationArn': 'arn:two'},
                                               {'DestinationArn': 'arn:three'}]}]}, {})
        result = check(gamelift, 'L-BB62CF1D')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'large')
        stub.assert_no_pending_responses()


def test_game_servers_use_the_largest_group():
    ctx = context('gamelift', 'L-51AF299A')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('list_game_server_groups',
                          {'GameServerGroups': [{'GameServerGroupName': 'group-a'}]}, {})
        stub.add_response('list_game_servers',
                          {'GameServers': [{'GameServerId': 'one'}, {'GameServerId': 'two'}]},
                          {'GameServerGroupName': 'group-a'})
        result = check(gamelift, 'L-51AF299A')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'group-a')
        stub.assert_no_pending_responses()


def test_macie_counts_buckets_across_every_bucket_definition():
    """A job may name buckets under several accounts; the quota counts them all."""
    ctx = context('macie2', 'L-14954719')
    with Stubber(ctx.client('macie2')) as stub:
        stub.add_response('list_classification_jobs', {'items': [{'jobId': 'job-1'}]}, {})
        stub.add_response('describe_classification_job', {
            'jobId': 'job-1', 'customDataIdentifierIds': ['cdi-1'],
            's3JobDefinition': {'bucketDefinitions': [
                {'accountId': '111111111111', 'buckets': ['one', 'two']},
                {'accountId': '222222222222', 'buckets': ['three']}]}}, {'jobId': 'job-1'})
        result = check(macie, 'L-14954719')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'job-1')
        stub.assert_no_pending_responses()


def test_macie_counts_custom_data_identifiers_per_job():
    ctx = context('macie2', 'L-3572300B')
    with Stubber(ctx.client('macie2')) as stub:
        stub.add_response('list_classification_jobs', {'items': [{'jobId': 'job-1'}]}, {})
        stub.add_response('describe_classification_job',
                          {'jobId': 'job-1', 'customDataIdentifierIds': ['cdi-1', 'cdi-2']},
                          {'jobId': 'job-1'})
        assert check(macie, 'L-3572300B')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
