from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import (autoscaling_plans, codecommit, rum, servicequotas,
                              shield, translate)
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)
ACCOUNT = '123456789012'


def uuid(suffix):
    return f'11111111-1111-1111-1111-1111111111{suffix:02d}'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def request(identity, status, service='ec2', quota='L-1216C47A'):
    return {'Id': identity, 'Status': status, 'ServiceCode': service,
            'QuotaCode': quota, 'DesiredValue': 10.0}


def test_only_undecided_quota_requests_are_active():
    ctx = context('servicequotas', 'L-89094105')
    with Stubber(ctx.client('service-quotas')) as stub:
        stub.add_response('list_requested_service_quota_change_history',
                          {'RequestedQuotas': [
                              request('r1', 'PENDING'), request('r2', 'CASE_OPENED'),
                              request('r3', 'APPROVED'), request('r4', 'DENIED'),
                              request('r5', 'CASE_CLOSED')]}, {})
        assert check(servicequotas, 'L-89094105')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_active_requests_are_also_reported_per_quota():
    ctx = context('servicequotas', 'L-36BDD542')
    with Stubber(ctx.client('service-quotas')) as stub:
        stub.add_response('list_requested_service_quota_change_history',
                          {'RequestedQuotas': [
                              request('r1', 'PENDING'),
                              request('r2', 'CASE_OPENED'),
                              request('r3', 'PENDING', 'lambda', 'L-B99A9384')]}, {})
        result = servicequotas.requests_per_quota(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'ec2/L-1216C47A')
        stub.assert_no_pending_responses()


def test_an_unknown_request_status_raises_nodata():
    ctx = context('servicequotas', 'L-89094105')
    with Stubber(ctx.client('service-quotas')) as stub:
        stub.add_response('list_requested_service_quota_change_history',
                          {'RequestedQuotas': [request('r1', 'DAYDREAMING')]}, {})
        with pytest.raises(NoData, match='unknown status'):
            check(servicequotas, 'L-89094105')(ctx)


def instruction(resource, configurations):
    return {'ServiceNamespace': 'ecs', 'ResourceId': resource,
            'ScalableDimension': 'ecs:service:DesiredCount',
            'MinCapacity': 1, 'MaxCapacity': 10,
            'TargetTrackingConfigurations': [
                {'TargetValue': 50.0 + index,
                 'PredefinedScalingMetricSpecification': {
                     'PredefinedScalingMetricType': 'ECSServiceAverageCPUUtilization'}}
                for index in range(configurations)]}


def plan(name, instructions):
    return {'ScalingPlanName': name, 'ScalingPlanVersion': 1,
            'ApplicationSource': {'CloudFormationStackARN': 'arn:aws:cloudformation:x'},
            'ScalingInstructions': instructions, 'StatusCode': 'Active'}


def test_scaling_plans_instructions_and_configurations_are_counted():
    plans = [plan('one', [instruction('service/a', 1)]),
             plan('two', [instruction('service/b', 3), instruction('service/c', 2)])]
    for module_check, expected_usage, expected_id in (
            ('L-BD401546', 2, None), ('L-7FAA513E', 2, 'two'),
            ('L-6538FA5E', 3, 'two/service/b')):
        ctx = context('autoscaling-plans', module_check)
        with Stubber(ctx.client('autoscaling-plans')) as stub:
            stub.add_response('describe_scaling_plans', {'ScalingPlans': plans}, {})
            result = check(autoscaling_plans, module_check)(ctx)
            assert result['usage'] == expected_usage, module_check
            assert result.get('resource_id') == expected_id, module_check
            stub.assert_no_pending_responses()


def protection(identity, arn):
    return {'Id': uuid(identity), 'Name': f'p{identity}', 'ResourceArn': arn}


def test_shield_protections_are_split_by_protected_resource_type():
    protections = [
        protection(1, f'arn:aws:ec2:eu-central-1:{ACCOUNT}:eip-allocation/eipalloc-1'),
        protection(2, f'arn:aws:ec2:eu-central-1:{ACCOUNT}:eip-allocation/eipalloc-2'),
        protection(3, f'arn:aws:elasticloadbalancing:eu-central-1:{ACCOUNT}:'
                         'loadbalancer/app/web/1234567890abcdef'),
        protection(4, f'arn:aws:cloudfront::{ACCOUNT}:distribution/E1234567890')]
    for code, expected in (('L-0BACF966', 2), ('L-BBD47253', 1)):
        ctx = context('shield', code)
        with Stubber(ctx.client('shield')) as stub:
            stub.add_response('list_protections', {'Protections': protections}, {})
            assert check(shield, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_a_protection_without_a_resource_arn_raises_nodata():
    ctx = context('shield', 'L-0BACF966')
    with Stubber(ctx.client('shield')) as stub:
        stub.add_response('list_protections', {'Protections': [
            {'Id': uuid(1), 'Name': 'p1'}]}, {})
        with pytest.raises(NoData, match='no resource ARN'):
            check(shield, 'L-0BACF966')(ctx)


def translation_job(identity, status):
    return {'JobId': identity, 'JobName': identity, 'JobStatus': status,
            'SubmittedTime': NOW}


def test_only_running_translation_jobs_are_concurrent():
    ctx = context('translate', 'L-10DB0BCF')
    with Stubber(ctx.client('translate')) as stub:
        stub.add_response('list_text_translation_jobs',
                          {'TextTranslationJobPropertiesList': [
                              translation_job('j1', 'IN_PROGRESS'),
                              translation_job('j2', 'SUBMITTED'),
                              translation_job('j3', 'STOP_REQUESTED'),
                              translation_job('j4', 'COMPLETED'),
                              translation_job('j5', 'FAILED')]}, {})
        assert translate.concurrent_batch_jobs(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_simple_inventories_are_counted_directly():
    for module, service, code, client, method, key, item in (
            (translate, 'translate', 'L-4011ABD8', 'translate', 'list_terminologies',
             'TerminologyPropertiesList', {'Name': 'glossary'}),
            (rum, 'rum', 'L-3FB7EA17', 'rum', 'list_app_monitors',
             'AppMonitorSummaries', {'Id': uuid(1), 'Name': 'web'}),
            (codecommit, 'codecommit', 'L-81790602', 'codecommit', 'list_repositories',
             'repositories', {'repositoryName': 'repo', 'repositoryId': 'r1'})):
        ctx = context(service, code)
        with Stubber(ctx.client(client)) as stub:
            stub.add_response(method, {key: [item, dict(item)]}, {})
            assert check(module, code)(ctx)['usage'] == 2, service
            stub.assert_no_pending_responses()


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((servicequotas, 'servicequotas'),
                            (autoscaling_plans, 'autoscaling-plans'),
                            (shield, 'shield'), (translate, 'translate'),
                            (rum, 'rum'), (codecommit, 'codecommit')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
