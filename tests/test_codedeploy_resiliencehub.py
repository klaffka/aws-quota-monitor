from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import codedeploy, resiliencehub
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
NOW = datetime(2026, 9, 15, tzinfo=UTC)
APPLICATION = 'shop'
GROUP = 'production'
APP = f'arn:aws:resiliencehub:eu-central-1:{ACCOUNT}:app/one'
OTHER_APP = f'arn:aws:resiliencehub:eu-central-1:{ACCOUNT}:app/two'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def stub_group(stub, detail, application=APPLICATION, group=GROUP):
    stub.add_response('list_applications', {'applications': [application]}, {})
    stub.add_response('list_deployment_groups',
                      {'applicationName': application, 'deploymentGroups': [group]},
                      {'applicationName': application})
    stub.add_response('get_deployment_group', {'deploymentGroupInfo': dict(
        {'applicationName': application, 'deploymentGroupName': group}, **detail)},
        {'applicationName': application, 'deploymentGroupName': group})


def test_alarms_auto_scaling_groups_and_triggers_are_counted_per_group():
    detail = {
        'alarmConfiguration': {'enabled': True, 'alarms': [
            {'name': 'cpu'}, {'name': 'errors'}]},
        'autoScalingGroups': [{'name': 'asg-1'}],
        'triggerConfigurations': [
            {'triggerName': 't1', 'triggerTargetArn':
             f'arn:aws:sns:eu-central-1:{ACCOUNT}:deploys',
             'triggerEvents': ['DeploymentSuccess']},
            {'triggerName': 't2', 'triggerTargetArn':
             f'arn:aws:sns:eu-central-1:{ACCOUNT}:alerts',
             'triggerEvents': ['DeploymentFailure']},
            {'triggerName': 't3', 'triggerTargetArn':
             f'arn:aws:sns:eu-central-1:{ACCOUNT}:audit',
             'triggerEvents': ['DeploymentStart']}],
    }
    for code, expected in (('L-9F835576', 2), ('L-6DACB4EE', 1), ('L-877B748B', 3)):
        ctx = context('codedeploy', code)
        with Stubber(ctx.client('codedeploy')) as stub:
            stub_group(stub, detail)
            result = check(codedeploy, code)(ctx)
            assert (result['usage'], result['resource_id']) == (
                expected, f'{APPLICATION}/{GROUP}'), code
            stub.assert_no_pending_responses()


def test_deployment_groups_are_counted_per_ecs_service():
    ctx = context('codedeploy', 'L-0CB3C26F')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_applications', {'applications': [APPLICATION]}, {})
        stub.add_response('list_deployment_groups',
                          {'applicationName': APPLICATION,
                           'deploymentGroups': [GROUP, 'canary']},
                          {'applicationName': APPLICATION})
        for group in (GROUP, 'canary'):
            stub.add_response('get_deployment_group', {'deploymentGroupInfo': {
                'applicationName': APPLICATION, 'deploymentGroupName': group,
                'ecsServices': [{'clusterName': 'main', 'serviceName': 'web'}]}},
                {'applicationName': APPLICATION, 'deploymentGroupName': group})
        result = codedeploy.deployment_groups_per_ecs_service(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'main/web')
        stub.assert_no_pending_responses()


def test_only_customer_deployment_configurations_are_counted():
    ctx = context('codedeploy', 'L-5AD34096')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_deployment_configs', {'deploymentConfigsList': [
            'CodeDeployDefault.AllAtOnce', 'CodeDeployDefault.OneAtATime',
            'SlowCanary']}, {})
        assert codedeploy.custom_deployment_configurations(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_concurrent_deployments_ask_aws_to_filter_by_status():
    ctx = context('codedeploy', 'L-AB125F0B')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_deployments', {'deployments': ['d-1', 'd-2']},
                          {'includeOnlyStatuses': codedeploy.RUNNING_STATES})
        assert codedeploy.concurrent_deployments(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def app_summary(arn):
    return {'appArn': arn, 'name': arn.rsplit('/', 1)[-1], 'creationTime': NOW,
            'complianceStatus': 'PolicyMet', 'status': 'Active'}


def assessment(arn, status, app=APP):
    return {'appArn': app, 'assessmentArn': arn, 'assessmentStatus': status,
            'invoker': 'User'}


def test_concurrent_assessments_are_counted_per_account_and_application():
    assessments = [
        assessment('arn:aws:resiliencehub:::assessment/1', 'InProgress'),
        assessment('arn:aws:resiliencehub:::assessment/2', 'Pending'),
        assessment('arn:aws:resiliencehub:::assessment/3', 'Success'),
        assessment('arn:aws:resiliencehub:::assessment/4', 'InProgress', OTHER_APP)]
    ctx = context('resiliencehub', 'L-BD955A74')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_app_assessments',
                          {'assessmentSummaries': assessments}, {})
        assert check(resiliencehub, 'L-BD955A74')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()
    ctx = context('resiliencehub', 'L-0AD966B7')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_apps', {'appSummaries': [
            app_summary(APP), app_summary(OTHER_APP)]}, {})
        stub.add_response('list_app_assessments',
                          {'assessmentSummaries': assessments}, {})
        result = check(resiliencehub, 'L-0AD966B7')(ctx)
        assert (result['usage'], result['resource_id']) == (2, APP)
        stub.assert_no_pending_responses()


def test_an_unknown_assessment_status_raises_nodata():
    ctx = context('resiliencehub', 'L-BD955A74')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_app_assessments', {'assessmentSummaries': [
            assessment('arn:aws:resiliencehub:::assessment/1', 'Snoozing')]}, {})
        with pytest.raises(NoData, match='unknown status'):
            check(resiliencehub, 'L-BD955A74')(ctx)


def test_application_components_use_the_newest_application_version():
    ctx = context('resiliencehub', 'L-0076B5C6')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_apps', {'appSummaries': [app_summary(APP)]}, {})
        stub.add_response('list_app_versions', {'appVersions': [
            {'appVersion': '1'}, {'appVersion': 'release'}]}, {'appArn': APP})
        stub.add_response('list_app_version_app_components', {
            'appArn': APP, 'appVersion': 'release', 'appComponents': [
                {'name': 'web', 'type': 'AWS::ResilienceHub::ComputeAppComponent'},
                {'name': 'db', 'type': 'AWS::ResilienceHub::DatabaseAppComponent'}]},
            {'appArn': APP, 'appVersion': 'release'})
        result = check(resiliencehub, 'L-0076B5C6')(ctx)
        assert (result['usage'], result['resource_id']) == (2, APP)
        stub.assert_no_pending_responses()


def test_an_application_without_a_version_raises_nodata():
    ctx = context('resiliencehub', 'L-0076B5C6')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_apps', {'appSummaries': [app_summary(APP)]}, {})
        stub.add_response('list_app_versions', {'appVersions': []}, {'appArn': APP})
        with pytest.raises(NoData, match='no version'):
            check(resiliencehub, 'L-0076B5C6')(ctx)


def test_every_check_is_registered_for_reporting():
    for module, service in ((codedeploy, 'codedeploy'),
                            (resiliencehub, 'resiliencehub')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
