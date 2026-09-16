import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import (appflow, connect_campaigns, ec2_fastlaunch,
                              inspector_classic, migrationhuborchestrator)
from modules.qmchecks import license_manager_linux_subscriptions as linux_subs
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
INSTANCE = '11111111-1111-1111-1111-111111111111'
OTHER_INSTANCE = '22222222-2222-2222-2222-222222222222'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_appflow_counts_flows_and_connector_profiles_once():
    for code, method, key, field in (
            ('L-A847D5B6', 'list_flows', 'flows', 'flowName'),
            ('L-0F8AA170', 'describe_connector_profiles', 'connectorProfileDetails',
             'connectorProfileName')):
        ctx = context('appflow', code)
        with Stubber(ctx.client('appflow')) as stub:
            stub.add_response(method, {key: [{field: 'a'}, {field: 'b'}, {field: 'a'}]}, {})
            assert check(appflow, code)(ctx)['usage'] == 2, code
            stub.assert_no_pending_responses()


def test_an_appflow_entry_without_a_name_raises_nodata():
    ctx = context('appflow', 'L-A847D5B6')
    with Stubber(ctx.client('appflow')) as stub:
        stub.add_response('list_flows', {'flows': [{'description': 'no name'}]}, {})
        with pytest.raises(NoData, match='missing its name'):
            check(appflow, 'L-A847D5B6')(ctx)


def test_inspector_classic_counts_each_assessment_arn_once():
    for code, method, key in (
            ('L-E1AFB5F4', 'list_assessment_targets', 'assessmentTargetArns'),
            ('L-7A3AEC10', 'list_assessment_templates', 'assessmentTemplateArns'),
            ('L-12943E2F', 'list_assessment_runs', 'assessmentRunArns')):
        ctx = context('inspector', code)
        with Stubber(ctx.client('inspector')) as stub:
            arn = f'arn:aws:inspector:eu-central-1:{ACCOUNT}:target/0-abcdefgh'
            stub.add_response(method, {key: [arn, f'{arn}2', arn]}, {})
            assert check(inspector_classic, code)(ctx)['usage'] == 2, code
            stub.assert_no_pending_responses()


def campaign(identity, instance=INSTANCE):
    return {'id': identity, 'arn': f'arn:aws:connect-campaigns:eu-central-1:'
                                   f'{ACCOUNT}:campaign/{identity}',
            'name': identity, 'connectInstanceId': instance,
            'channelSubtypes': ['TELEPHONY']}


def test_campaigns_are_counted_per_connect_instance():
    ctx = context('connect-campaigns', 'L-31C1321D')
    with Stubber(ctx.client('connectcampaignsv2')) as stub:
        stub.add_response('list_campaigns', {'campaignSummaryList': [
            campaign('c1'), campaign('c2'), campaign('c3', OTHER_INSTANCE)]}, {})
        result = connect_campaigns.total_campaigns_per_instance(ctx)
        assert (result['usage'], result['resource_id']) == (2, INSTANCE)
        stub.assert_no_pending_responses()


def test_only_running_paused_or_initialized_campaigns_are_active():
    ctx = context('connect-campaigns', 'L-7F7B4C39')
    with Stubber(ctx.client('connectcampaignsv2')) as stub:
        stub.add_response('list_campaigns', {'campaignSummaryList': [
            campaign('c1'), campaign('c2'), campaign('c3')]}, {})
        stub.add_response('get_campaign_state_batch', {'successfulRequests': [
            {'campaignId': 'c1', 'state': 'Running'},
            {'campaignId': 'c2', 'state': 'Paused'},
            {'campaignId': 'c3', 'state': 'Completed'}]},
            {'campaignIds': ['c1', 'c2', 'c3']})
        result = connect_campaigns.active_campaigns_per_instance(ctx)
        assert (result['usage'], result['resource_id']) == (2, INSTANCE)
        stub.assert_no_pending_responses()


def test_a_campaign_state_that_cannot_be_read_raises_nodata():
    ctx = context('connect-campaigns', 'L-7F7B4C39')
    with Stubber(ctx.client('connectcampaignsv2')) as stub:
        stub.add_response('list_campaigns', {'campaignSummaryList': [campaign('c1')]}, {})
        stub.add_response('get_campaign_state_batch', {
            'successfulRequests': [],
            'failedRequests': [{'campaignId': 'c1', 'failureCode': 'ResourceNotFound'}]},
            {'campaignIds': ['c1']})
        with pytest.raises(NoData, match='could not be read'):
            connect_campaigns.active_campaigns_per_instance(ctx)


def test_migration_workflows_step_groups_and_steps_are_counted():
    ctx = context('migrationhuborchestrator', 'L-71F71C2E')
    with Stubber(ctx.client('migrationhuborchestrator')) as stub:
        stub.add_response('list_workflows', {'migrationWorkflowSummary': [
            {'id': 'wf-1', 'name': 'one'}]}, {})
        stub.add_response('list_workflow_step_groups', {'workflowStepGroupsSummary': [
            {'id': 'sg-1', 'name': 'first'}, {'id': 'sg-2', 'name': 'second'}]},
            {'workflowId': 'wf-1'})
        stub.add_response('list_workflow_steps', {'workflowStepsSummary': [
            {'stepId': 's1', 'name': 'a', 'stepActionType': 'MANUAL',
             'owner': 'AWS_MANAGED', 'status': 'READY'}]},
            {'workflowId': 'wf-1', 'stepGroupId': 'sg-1'})
        stub.add_response('list_workflow_steps', {'workflowStepsSummary': [
            {'stepId': 's2', 'name': 'b', 'stepActionType': 'MANUAL',
             'owner': 'AWS_MANAGED', 'status': 'READY'},
            {'stepId': 's3', 'name': 'c', 'stepActionType': 'MANUAL',
             'owner': 'AWS_MANAGED', 'status': 'READY'}]},
            {'workflowId': 'wf-1', 'stepGroupId': 'sg-2'})
        result = migrationhuborchestrator.steps_per_step_group(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'wf-1/sg-2')
        stub.assert_no_pending_responses()


def test_linux_subscription_instances_are_counted_once():
    ctx = context('license-manager-linux-subscriptions', 'L-5373D1AB')
    with Stubber(ctx.client('license-manager-linux-subscriptions')) as stub:
        stub.add_response('list_linux_subscription_instances', {'Instances': [
            {'InstanceID': 'i-1'}, {'InstanceID': 'i-2'}, {'InstanceID': 'i-1'}]}, {})
        assert linux_subs.discovered_resources(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_parallel_launches_report_the_largest_configured_image():
    ctx = context('ec2fastlaunch', 'L-DC79B53E')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_fast_launch_images', {'FastLaunchImages': [
            {'ImageId': 'ami-00000000000000001', 'MaxParallelLaunches': 6,
             'State': 'enabled'},
            {'ImageId': 'ami-00000000000000002', 'MaxParallelLaunches': 10,
             'State': 'enabled'}]}, {})
        result = ec2_fastlaunch.parallel_launches(ctx)
        assert (result['usage'], result['resource_id']) == (10, 'ami-00000000000000002')
        stub.assert_no_pending_responses()


def test_a_fast_launch_image_without_a_count_raises_nodata():
    ctx = context('ec2fastlaunch', 'L-DC79B53E')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_fast_launch_images', {'FastLaunchImages': [
            {'ImageId': 'ami-00000000000000001', 'State': 'enabled'}]}, {})
        with pytest.raises(NoData, match='no parallel launch count'):
            ec2_fastlaunch.parallel_launches(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in (
            (appflow, 'appflow'), (inspector_classic, 'inspector'),
            (connect_campaigns, 'connect-campaigns'),
            (migrationhuborchestrator, 'migrationhuborchestrator'),
            (linux_subs, 'license-manager-linux-subscriptions'),
            (ec2_fastlaunch, 'ec2fastlaunch')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
