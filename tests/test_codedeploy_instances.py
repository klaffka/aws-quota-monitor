import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import codedeploy
from modules.qmcore.aws import CheckContext, NoData

RUNNING = ['Created', 'Queued', 'InProgress', 'Baking', 'Ready']


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'codedeploy', 'QuotaCode': code,
                          'Value': 1000}], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in codedeploy.CHECKS if candidate == code)


def deployment(identity, platform):
    return {'deploymentId': identity, 'computePlatform': platform,
            'status': 'InProgress'}


def test_only_server_deployments_consume_instances():
    ctx = context('L-464411D9')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_deployments', {'deployments': ['d-1', 'd-2', 'd-3']},
                          {'includeOnlyStatuses': RUNNING})
        stub.add_response('batch_get_deployments', {'deploymentsInfo': [
            deployment('d-1', 'Server'), deployment('d-2', 'Server'),
            deployment('d-3', 'Lambda')]},
            {'deploymentIds': ['d-1', 'd-2', 'd-3']})
        stub.add_response('list_deployment_targets',
                          {'targetIds': ['i-1', 'i-2', 'i-3']}, {'deploymentId': 'd-1'})
        stub.add_response('list_deployment_targets', {'targetIds': ['i-4']},
                          {'deploymentId': 'd-2'})
        assert check('L-464411D9')(ctx)['usage'] == 4
        largest = check('L-6BCCFC85')(ctx)
        assert (largest['usage'], largest['resource_id']) == (3, 'd-1')
        stub.assert_no_pending_responses()


def test_an_undescribed_deployment_raises_nodata():
    ctx = context('L-464411D9')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_deployments', {'deployments': ['d-1', 'd-2']},
                          {'includeOnlyStatuses': RUNNING})
        stub.add_response('batch_get_deployments',
                          {'deploymentsInfo': [deployment('d-1', 'Server')]},
                          {'deploymentIds': ['d-1', 'd-2']})
        with pytest.raises(NoData, match='every running deployment'):
            check('L-464411D9')(ctx)


def test_an_unknown_compute_platform_raises_nodata():
    ctx = context('L-464411D9')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_deployments', {'deployments': ['d-1']},
                          {'includeOnlyStatuses': RUNNING})
        stub.add_response('batch_get_deployments',
                          {'deploymentsInfo': [deployment('d-1', 'Mainframe')]},
                          {'deploymentIds': ['d-1']})
        with pytest.raises(NoData, match='unknown compute platform'):
            check('L-464411D9')(ctx)


def test_listeners_are_counted_for_each_traffic_route():
    ctx = context('L-C77AFF36')
    listener = 'arn:aws:elasticloadbalancing:eu-central-1:123456789012:listener/app/one/1/'
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_applications', {'applications': ['app']}, {})
        stub.add_response('list_deployment_groups',
                          {'applicationName': 'app', 'deploymentGroups': ['group']},
                          {'applicationName': 'app'})
        stub.add_response('get_deployment_group', {'deploymentGroupInfo': {
            'applicationName': 'app', 'deploymentGroupName': 'group',
            'loadBalancerInfo': {'targetGroupPairInfoList': [{
                'targetGroups': [{'name': 'one'}, {'name': 'two'}],
                'prodTrafficRoute': {'listenerArns': [listener + '1',
                                                      listener + '2']},
                'testTrafficRoute': {'listenerArns': [listener + '3']}}]}}},
            {'applicationName': 'app', 'deploymentGroupName': 'group'})
        result = check('L-C77AFF36')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'app/group#0/prodTrafficRoute')
        stub.assert_no_pending_responses()


def test_github_tokens_are_counted():
    ctx = context('L-B0CB7B38')
    with Stubber(ctx.client('codedeploy')) as stub:
        stub.add_response('list_git_hub_account_token_names',
                          {'tokenNameList': ['one', 'two']}, {})
        assert check('L-B0CB7B38')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
