"""Direct Connect connection scopes and AWS Batch queue scopes."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import batch, directconnect
from modules.qmcore.aws import CheckContext, NoData


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def connection(identity, hosted=False, lag=None):
    entry = {'connectionId': identity, 'connectionName': identity,
             'connectionState': 'available', 'location': 'EqFr5'}
    if hosted:
        entry['partnerName'] = 'A Partner'
    if lag:
        entry['lagId'] = lag
    return entry


CONNECTIONS = {'connections': [
    connection('dxcon-hosted', hosted=True, lag='dxlag-one'),
    connection('dxcon-dedicated', lag='dxlag-one'),
    connection('dxcon-lonely', hosted=True)]}


def virtual_interfaces(count):
    return {'virtualInterfaces': [
        {'virtualInterfaceId': f'dxvif-{index}', 'virtualInterfaceType': 'private'}
        for index in range(count)]}


def stub_walk(stub, counts):
    stub.add_response('describe_connections', CONNECTIONS, {})
    for identity, count in counts.items():
        stub.add_response('describe_virtual_interfaces', virtual_interfaces(count),
                          {'connectionId': identity})


def test_only_hosted_connections_hold_the_hosted_quota():
    """A dedicated connection holds a different quota of its own."""
    ctx = context('directconnect', 'L-3745876E')
    with Stubber(ctx.client('directconnect')) as stub:
        stub_walk(stub, {'dxcon-hosted': 2, 'dxcon-dedicated': 9, 'dxcon-lonely': 3})
        result = check('L-3745876E', directconnect.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'dxcon-lonely')
        stub.assert_no_pending_responses()


def test_interfaces_are_summed_across_the_connections_of_a_lag():
    """A LAG bundles connections, so its interfaces are all of theirs."""
    ctx = context('directconnect', 'L-59AD3548')
    with Stubber(ctx.client('directconnect')) as stub:
        stub_walk(stub, {'dxcon-hosted': 2, 'dxcon-dedicated': 9, 'dxcon-lonely': 3})
        result = check('L-59AD3548', directconnect.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (11, 'dxlag-one')
        stub.assert_no_pending_responses()


def test_a_connection_without_an_identity_is_reported():
    ctx = context('directconnect', 'L-59AD3548')
    with Stubber(ctx.client('directconnect')) as stub:
        stub.add_response('describe_connections',
                          {'connections': [{'connectionName': 'nameless'}]}, {})
        with pytest.raises(NoData, match='identity'):
            check('L-59AD3548', directconnect.CHECKS)(ctx)


def queue(name, environments=0, policy=None):
    entry = {'jobQueueName': name, 'jobQueueArn': f'arn:queue/{name}', 'state': 'ENABLED',
             'priority': 1, 'computeEnvironmentOrder': [],
             'serviceEnvironmentOrder': [
                 {'order': index, 'serviceEnvironment': f'arn:env/{index}'}
                 for index in range(environments)]}
    if policy:
        entry['schedulingPolicyArn'] = policy
    return entry


def test_service_environments_are_counted_per_job_queue():
    ctx = context('batch', 'L-80D92D24')
    with Stubber(ctx.client('batch')) as stub:
        stub.add_response('describe_job_queues', {'jobQueues': [
            queue('wide', environments=3), queue('narrow', environments=1)]}, {})
        result = check('L-80D92D24', batch.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'wide')
        stub.assert_no_pending_responses()


def test_share_identifiers_come_from_the_policy_a_queue_names():
    """A queue without a scheduling policy has no share identifiers at all."""
    ctx = context('batch', 'L-C997A649')
    with Stubber(ctx.client('batch')) as stub:
        stub.add_response('describe_job_queues', {'jobQueues': [
            queue('fair', policy='arn:policy/fair'), queue('plain')]}, {})
        stub.add_response('describe_scheduling_policies', {'schedulingPolicies': [
            {'name': 'fair', 'arn': 'arn:policy/fair', 'fairsharePolicy': {
                'shareDistribution': [{'shareIdentifier': 'a'}, {'shareIdentifier': 'b'}]}}]},
            {'arns': ['arn:policy/fair']})
        result = check('L-C997A649', batch.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'fair')
        stub.assert_no_pending_responses()


def test_service_environments_are_counted_for_the_account():
    ctx = context('batch', 'L-61E3E54E')
    with Stubber(ctx.client('batch')) as stub:
        stub.add_response('describe_service_environments', {'serviceEnvironments': [
            {'serviceEnvironmentName': 'one', 'serviceEnvironmentArn': 'arn:env/one',
             'serviceEnvironmentType': 'SAGEMAKER_TRAINING', 'state': 'ENABLED',
             'capacityLimits': [{'maxCapacity': 10, 'capacityUnit': 'NUM_INSTANCES'}]}]}, {})
        assert check('L-61E3E54E', batch.CHECKS)(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
