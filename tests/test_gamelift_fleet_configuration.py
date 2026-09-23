"""GameLift fleet configuration limits, read from the fleet itself."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import gamelift
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'gamelift', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in gamelift.CHECKS if quota == code)


def fleet(identity, creator=None, minutes=None, compute='EC2'):
    entry = {'FleetId': identity, 'FleetArn': f'arn:fleet/{identity}',
             'ComputeType': compute, 'Status': 'ACTIVE', 'CreationTime': MOMENT}
    if creator is not None or minutes is not None:
        policy = {}
        if creator is not None:
            policy['NewGameSessionsPerCreator'] = creator
        if minutes is not None:
            policy['PolicyPeriodInMinutes'] = minutes
        entry['ResourceCreationLimitPolicy'] = policy
    return entry


@pytest.mark.parametrize('code, expected, resource', [
    ('L-3A43EF3C', 7, 'busy'),    # NewGameSessionsPerCreator
    ('L-9F9DE0B2', 60, 'slow'),   # PolicyPeriodInMinutes
])
def test_the_creation_limit_policy_is_read_from_each_fleet(code, expected, resource):
    ctx = context(code)
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes', {'FleetAttributes': [
            fleet('busy', creator=7, minutes=5),
            fleet('slow', creator=1, minutes=60),
            fleet('unset')]}, {})
        result = check(code)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, resource)
        stub.assert_no_pending_responses()


def test_a_fleet_without_a_creation_limit_policy_counts_as_zero():
    """AWS applies no limit unless the fleet configures one."""
    ctx = context('L-3A43EF3C')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes',
                          {'FleetAttributes': [fleet('unset')]}, {})
        assert check('L-3A43EF3C')(ctx)['usage'] == 0


def test_server_processes_count_their_concurrent_executions():
    """The quota bounds processes per instance, not entries in the config."""
    ctx = context('L-C30AA854')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes', {'FleetAttributes': [
            fleet('one'), fleet('two')]}, {})
        stub.add_response('describe_runtime_configuration', {'RuntimeConfiguration': {
            'ServerProcesses': [{'LaunchPath': '/local/game/a', 'ConcurrentExecutions': 3},
                                {'LaunchPath': '/local/game/b', 'ConcurrentExecutions': 2}]}},
            {'FleetId': 'one'})
        stub.add_response('describe_runtime_configuration', {'RuntimeConfiguration': {
            'ServerProcesses': [{'LaunchPath': '/local/game/c', 'ConcurrentExecutions': 4}]}},
            {'FleetId': 'two'})
        result = check('L-C30AA854')(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'one')
        stub.assert_no_pending_responses()


def test_a_server_process_without_a_count_is_reported():
    """Driven through a stand-in, because the response shape makes the count
    required and Stubber will not send one without it."""
    from unittest.mock import Mock
    ctx = Mock()
    ctx.call.side_effect = [
        [fleet('one')],
        {'RuntimeConfiguration': {'ServerProcesses': [{'LaunchPath': '/local/game/a'}]}}]
    with pytest.raises(NoData, match='concurrent executions'):
        gamelift.server_processes_per_instance(ctx)


def test_an_anywhere_fleet_has_no_runtime_configuration_to_read():
    """Only a managed EC2 fleet runs server processes GameLift configures."""
    ctx = context('L-C30AA854')
    with Stubber(ctx.client('gamelift')) as stub:
        stub.add_response('describe_fleet_attributes',
                          {'FleetAttributes': [fleet('anywhere', compute='ANYWHERE')]}, {})
        assert check('L-C30AA854')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()
