"""Auto Scaling group scopes and Cognito user pool scopes."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import autoscaling, cognito
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=timezone.utc)


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def group(name, load_balancers=(), target_groups=()):
    return {'AutoScalingGroupName': name, 'MinSize': 0, 'MaxSize': 1,
            'DesiredCapacity': 0, 'DefaultCooldown': 300, 'AvailabilityZones': ['eu-central-1a'],
            'HealthCheckType': 'EC2', 'CreatedTime': MOMENT,
            'LoadBalancerNames': list(load_balancers),
            'TargetGroupARNs': list(target_groups)}


GROUPS = {'AutoScalingGroups': [
    group('busy', load_balancers=['a', 'b'], target_groups=['arn:tg/1']),
    group('quiet', load_balancers=['c'], target_groups=['arn:tg/2', 'arn:tg/3'])]}


@pytest.mark.parametrize('code, expected, resource', [
    ('L-F786B2E5', 2, 'busy'),    # Classic Load Balancers per group
    ('L-05CB8B12', 2, 'quiet'),   # Target groups per group
])
def test_the_group_listing_already_carries_its_attachments(code, expected, resource):
    ctx = context('autoscaling', code)
    with Stubber(ctx.client('autoscaling')) as stub:
        stub.add_response('describe_auto_scaling_groups', GROUPS, {})
        result = check(code, autoscaling.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, resource)
        stub.assert_no_pending_responses()


def test_scaling_policies_are_grouped_by_the_group_they_name():
    """DescribePolicies answers for the whole account and names each group."""
    ctx = context('autoscaling', 'L-72753F6F')
    with Stubber(ctx.client('autoscaling')) as stub:
        stub.add_response('describe_policies', {'ScalingPolicies': [
            {'AutoScalingGroupName': 'busy', 'PolicyName': 'one', 'PolicyType': 'SimpleScaling'},
            {'AutoScalingGroupName': 'busy', 'PolicyName': 'two', 'PolicyType': 'StepScaling'},
            {'AutoScalingGroupName': 'quiet', 'PolicyName': 'three',
             'PolicyType': 'SimpleScaling'}]}, {})
        result = check('L-72753F6F', autoscaling.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'busy')
        stub.assert_no_pending_responses()


def test_step_adjustments_are_counted_per_policy_not_per_group():
    ctx = context('autoscaling', 'L-6C2A2F6E')
    with Stubber(ctx.client('autoscaling')) as stub:
        stub.add_response('describe_policies', {'ScalingPolicies': [
            {'AutoScalingGroupName': 'busy', 'PolicyName': 'one', 'PolicyType': 'StepScaling',
             'StepAdjustments': [{'ScalingAdjustment': 1}, {'ScalingAdjustment': 2},
                                 {'ScalingAdjustment': 3}]},
            {'AutoScalingGroupName': 'busy', 'PolicyName': 'two',
             'PolicyType': 'TargetTrackingScaling'}]}, {})
        result = check('L-6C2A2F6E', autoscaling.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'busy/one')
        stub.assert_no_pending_responses()


def test_one_topic_notified_about_two_events_is_still_one_topic():
    """DescribeNotificationConfigurations returns a row per event type."""
    ctx = context('autoscaling', 'L-CEE5E714')
    with Stubber(ctx.client('autoscaling')) as stub:
        stub.add_response('describe_notification_configurations',
                          {'NotificationConfigurations': [
                              {'AutoScalingGroupName': 'busy', 'TopicARN': 'arn:sns/one',
                               'NotificationType': 'autoscaling:EC2_INSTANCE_LAUNCH'},
                              {'AutoScalingGroupName': 'busy', 'TopicARN': 'arn:sns/one',
                               'NotificationType': 'autoscaling:EC2_INSTANCE_TERMINATE'},
                              {'AutoScalingGroupName': 'busy', 'TopicARN': 'arn:sns/two',
                               'NotificationType': 'autoscaling:EC2_INSTANCE_LAUNCH'}]}, {})
        result = check('L-CEE5E714', autoscaling.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'busy')
        stub.assert_no_pending_responses()


def test_lifecycle_hooks_are_asked_for_per_group():
    ctx = context('autoscaling', 'L-1312BBBF')
    with Stubber(ctx.client('autoscaling')) as stub:
        stub.add_response('describe_auto_scaling_groups', GROUPS, {})
        stub.add_response('describe_lifecycle_hooks', {'LifecycleHooks': [
            {'LifecycleHookName': 'a', 'AutoScalingGroupName': 'busy'}]},
            {'AutoScalingGroupName': 'busy'})
        stub.add_response('describe_lifecycle_hooks', {'LifecycleHooks': []},
                          {'AutoScalingGroupName': 'quiet'})
        result = check('L-1312BBBF', autoscaling.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (1, 'busy')
        stub.assert_no_pending_responses()


POOLS = {'UserPools': [{'Id': 'eu-central-1_aaaaaaaaa', 'Name': 'one'},
                       {'Id': 'eu-central-1_bbbbbbbbb', 'Name': 'two'}]}


@pytest.mark.parametrize('code, method, key, payload, expected', [
    ('L-5EAB0605', 'list_user_pool_clients', 'UserPoolClients',
     [{'ClientId': 'c1'}, {'ClientId': 'c2'}], 2),
    ('L-A585C375', 'list_groups', 'Groups', [{'GroupName': 'g1'}], 1),
    ('L-1B44D826', 'list_identity_providers', 'Providers',
     [{'ProviderName': 'p1', 'ProviderType': 'SAML'}], 1),
])
def test_user_pool_scopes_take_the_largest_pool(code, method, key, payload, expected):
    ctx = context('cognito-idp', code)
    with Stubber(ctx.client('cognito-idp')) as stub:
        stub.add_response('list_user_pools', POOLS, {'MaxResults': 60})
        stub.add_response(method, {key: payload}, {'UserPoolId': 'eu-central-1_aaaaaaaaa'})
        stub.add_response(method, {key: []}, {'UserPoolId': 'eu-central-1_bbbbbbbbb'})
        result = check(code, cognito.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, 'eu-central-1_aaaaaaaaa')
        stub.assert_no_pending_responses()


def test_scopes_are_counted_per_resource_server_not_per_pool():
    ctx = context('cognito-idp', 'L-770A44F8')
    with Stubber(ctx.client('cognito-idp')) as stub:
        stub.add_response('list_user_pools', {'UserPools': [POOLS['UserPools'][0]]},
                          {'MaxResults': 60})
        stub.add_response('list_resource_servers', {'ResourceServers': [
            {'UserPoolId': 'eu-central-1_aaaaaaaaa', 'Identifier': 'api', 'Name': 'api',
             'Scopes': [{'ScopeName': 'read', 'ScopeDescription': 'r'},
                        {'ScopeName': 'write', 'ScopeDescription': 'w'}]},
            {'UserPoolId': 'eu-central-1_aaaaaaaaa', 'Identifier': 'bare', 'Name': 'bare'}]},
            {'UserPoolId': 'eu-central-1_aaaaaaaaa', 'MaxResults': 50})
        result = check('L-770A44F8', cognito.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'eu-central-1_aaaaaaaaa/api')
        stub.assert_no_pending_responses()


def test_a_user_pool_without_an_identity_is_reported():
    ctx = context('cognito-idp', 'L-A585C375')
    with Stubber(ctx.client('cognito-idp')) as stub:
        stub.add_response('list_user_pools', {'UserPools': [{'Name': 'nameless'}]},
                          {'MaxResults': 60})
        with pytest.raises(NoData, match='identity'):
            check('L-A585C375', cognito.CHECKS)(ctx)
