import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import codebuild
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
PROJECT = 'api'
OTHER_PROJECT = 'worker'


def context(code='L-ACCF6C0D'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'codebuild', 'QuotaCode': code, 'Value': 60}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _, fn in codebuild.CHECKS if quota == code)


def build(identity, status, environment='LINUX_CONTAINER',
          compute='BUILD_GENERAL1_SMALL'):
    return {'id': identity, 'buildStatus': status,
            'environment': {'type': environment, 'computeType': compute,
                            'image': 'aws/codebuild/standard:7.0'}}


def project(name, tags=(), subnets=(), security_groups=(), timeout=None):
    result = {'name': name, 'arn': f'arn:aws:codebuild:eu-central-1:{ACCOUNT}:'
                                   f'project/{name}',
              'tags': [{'key': f'k{index}', 'value': 'v'} for index in range(len(tags))]}
    if subnets or security_groups:
        result['vpcConfig'] = {'vpcId': 'vpc-1', 'subnets': list(subnets),
                               'securityGroupIds': list(security_groups)}
    if timeout is not None:
        result['timeoutInMinutes'] = timeout
    return result


def test_concurrent_builds_are_grouped_by_environment_and_compute_size():
    ctx = context('L-9D07B6EF')
    with Stubber(ctx.client('codebuild')) as stub:
        stub.add_response('list_builds', {'ids': ['b1', 'b2', 'b3', 'b4']},
                          {'sortOrder': 'DESCENDING'})
        stub.add_response('batch_get_builds', {'builds': [
            build('b1', 'IN_PROGRESS'),
            build('b2', 'IN_PROGRESS'),
            build('b3', 'SUCCEEDED'),
            build('b4', 'IN_PROGRESS', 'ARM_CONTAINER', 'BUILD_GENERAL1_LARGE')]},
            {'ids': ['b1', 'b2', 'b3', 'b4']})
        assert check('L-9D07B6EF')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_environment_without_a_running_build_reports_zero():
    ctx = context('L-36AF3CA5')
    with Stubber(ctx.client('codebuild')) as stub:
        stub.add_response('list_builds', {'ids': ['b1']}, {'sortOrder': 'DESCENDING'})
        stub.add_response('batch_get_builds', {'builds': [build('b1', 'IN_PROGRESS')]},
                          {'ids': ['b1']})
        assert check('L-36AF3CA5')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_an_unknown_build_status_raises_nodata():
    ctx = context('L-9D07B6EF')
    with Stubber(ctx.client('codebuild')) as stub:
        stub.add_response('list_builds', {'ids': ['b1']}, {'sortOrder': 'DESCENDING'})
        stub.add_response('batch_get_builds', {'builds': [build('b1', 'DREAMING')]},
                          {'ids': ['b1']})
        with pytest.raises(NoData, match='unknown status'):
            check('L-9D07B6EF')(ctx)


def test_a_running_build_at_the_end_of_the_window_raises_nodata(monkeypatch):
    # The scan is bounded, so a running build in the last batch may be truncated.
    monkeypatch.setattr(codebuild, 'SCANNED_BUILDS', 2)
    monkeypatch.setattr(codebuild, 'BATCH', 2)
    ctx = context('L-9D07B6EF')
    with Stubber(ctx.client('codebuild')) as stub:
        stub.add_response('list_builds', {'ids': ['b1', 'b2', 'b3']},
                          {'sortOrder': 'DESCENDING'})
        stub.add_response('batch_get_builds', {'builds': [
            build('b1', 'IN_PROGRESS'), build('b2', 'IN_PROGRESS')]},
            {'ids': ['b1', 'b2']})
        with pytest.raises(NoData, match='scanned window'):
            check('L-9D07B6EF')(ctx)


def test_project_tags_vpc_lists_and_timeout_report_the_largest_project():
    projects = [project(PROJECT, tags='ab', subnets=['subnet-1'],
                        security_groups=['sg-1', 'sg-2'], timeout=30),
                project(OTHER_PROJECT, tags='abcd',
                        subnets=['subnet-1', 'subnet-2', 'subnet-3'], timeout=480)]
    for code, expected_usage, expected_id in (
            ('L-BECF4531', 4, OTHER_PROJECT), ('L-EDB7A61A', 2, PROJECT),
            ('L-33638FE6', 3, OTHER_PROJECT), ('L-4167E76F', 480, OTHER_PROJECT)):
        ctx = context(code)
        with Stubber(ctx.client('codebuild')) as stub:
            stub.add_response('list_projects', {'projects': [PROJECT, OTHER_PROJECT]}, {})
            stub.add_response('batch_get_projects', {'projects': projects},
                              {'names': [PROJECT, OTHER_PROJECT]})
            result = check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def test_a_project_that_disappears_between_calls_raises_nodata():
    ctx = context('L-BECF4531')
    with Stubber(ctx.client('codebuild')) as stub:
        stub.add_response('list_projects', {'projects': [PROJECT]}, {})
        stub.add_response('batch_get_projects', {'projects': [],
                                                 'projectsNotFound': [PROJECT]},
                          {'names': [PROJECT]})
        with pytest.raises(NoData, match='disappeared'):
            check('L-BECF4531')(ctx)


def test_every_codebuild_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'codebuild'}
    assert {code for code, _, _ in codebuild.CHECKS} <= registered
