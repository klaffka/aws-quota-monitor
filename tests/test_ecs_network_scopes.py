"""ECS scopes that a service's deployment or a cluster's task list reports."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ecs
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'ecs', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in ecs.CHECKS if quota == code)


def cluster_arn(name):
    return f'arn:aws:ecs:{REGION}:{ACCOUNT}:cluster/{name}'


def service_arn(cluster, name):
    return f'arn:aws:ecs:{REGION}:{ACCOUNT}:service/{cluster}/{name}'


def task_arn(cluster, name):
    return f'arn:aws:ecs:{REGION}:{ACCOUNT}:task/{cluster}/{name}'


def service(cluster, name, namespace=None):
    """A described service; Service Connect lives on the active deployment."""
    deployment = {'id': f'ecs-svc/{name}', 'status': 'PRIMARY'}
    if namespace is not None:
        deployment['serviceConnectConfiguration'] = {'enabled': True,
                                                     'namespace': namespace}
    return {'serviceArn': service_arn(cluster, name), 'serviceName': name,
            'clusterArn': cluster_arn(cluster), 'deployments': [deployment]}


def stub_services(stub, clusters):
    """Stub the cluster walk, then the listing and describe of each service."""
    stub.add_response('list_clusters',
                      {'clusterArns': [cluster_arn(name) for name in clusters]}, {})
    for name, services in clusters.items():
        arns = [service_arn(name, entry['serviceName']) for entry in services]
        stub.add_response('list_services', {'serviceArns': arns},
                          {'cluster': cluster_arn(name)})
        if arns:
            stub.add_response('describe_services', {'services': services},
                              {'cluster': cluster_arn(name), 'services': arns})


def test_services_are_counted_per_service_connect_namespace():
    ctx = context('L-2D029656')
    with Stubber(ctx.client('ecs')) as stub:
        stub_services(stub, {
            'blue': [service('blue', 'one', 'shop'), service('blue', 'two', 'shop')],
            'green': [service('green', 'three', 'shop'),
                      service('green', 'four', 'billing')]})
        result = check('L-2D029656')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'shop')
        stub.assert_no_pending_responses()


def test_a_service_outside_service_connect_belongs_to_no_namespace():
    ctx = context('L-2D029656')
    with Stubber(ctx.client('ecs')) as stub:
        stub_services(stub, {'blue': [service('blue', 'one'),
                                      service('blue', 'two', 'shop')]})
        result = check('L-2D029656')(ctx)
        assert (result['usage'], result['resource_id']) == (1, 'shop')
        stub.assert_no_pending_responses()


def test_a_service_connect_deployment_without_a_namespace_is_reported():
    """Service Connect always names a namespace, so an absent one is not a zero."""
    ctx = context('L-2D029656')
    with Stubber(ctx.client('ecs')) as stub:
        stub_services(stub, {'blue': [
            {'serviceArn': service_arn('blue', 'one'), 'serviceName': 'one',
             'deployments': [{'id': 'ecs-svc/one',
                              'serviceConnectConfiguration': {'enabled': True}}]}]})
        with pytest.raises(NoData, match='namespace'):
            check('L-2D029656')(ctx)


def test_an_account_using_no_service_connect_counts_as_zero():
    ctx = context('L-2D029656')
    with Stubber(ctx.client('ecs')) as stub:
        stub_services(stub, {'blue': [service('blue', 'one')]})
        assert check('L-2D029656')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def stub_tasks(stub, clusters):
    """Stub the cluster walk, then each cluster's task listing and describe."""
    stub.add_response('list_clusters',
                      {'clusterArns': [cluster_arn(name) for name in clusters]}, {})
    for name, tasks in clusters.items():
        arns = [task_arn(name, entry['taskArn']) for entry in tasks]
        stub.add_response('list_tasks', {'taskArns': arns},
                          {'cluster': cluster_arn(name), 'desiredStatus': 'RUNNING'})
        if arns:
            stub.add_response('describe_tasks', {'tasks': [
                {'taskArn': task_arn(name, entry['taskArn']),
                 'clusterArn': cluster_arn(name),
                 'lastStatus': entry['lastStatus']} for entry in tasks]},
                {'cluster': cluster_arn(name), 'tasks': arns})


def test_only_the_tasks_still_provisioning_are_counted():
    ctx = context('L-B7718569')
    with Stubber(ctx.client('ecs')) as stub:
        stub_tasks(stub, {'busy': [
            {'taskArn': 'a', 'lastStatus': 'PROVISIONING'},
            {'taskArn': 'b', 'lastStatus': 'PROVISIONING'},
            {'taskArn': 'c', 'lastStatus': 'RUNNING'},
            {'taskArn': 'd', 'lastStatus': 'PENDING'}]})
        result = check('L-B7718569')(ctx)
        assert (result['usage'], result['resource_id']) == (2, cluster_arn('busy'))
        stub.assert_no_pending_responses()


def test_the_busiest_cluster_is_the_one_measured():
    ctx = context('L-B7718569')
    with Stubber(ctx.client('ecs')) as stub:
        stub_tasks(stub, {
            'quiet': [{'taskArn': 'a', 'lastStatus': 'PROVISIONING'}],
            'busy': [{'taskArn': 'b', 'lastStatus': 'PROVISIONING'},
                     {'taskArn': 'c', 'lastStatus': 'PROVISIONING'}]})
        result = check('L-B7718569')(ctx)
        assert (result['usage'], result['resource_id']) == (2, cluster_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_cluster_running_nothing_counts_as_zero():
    """An empty cluster still holds the quota, so it stays in the maximum."""
    ctx = context('L-B7718569')
    with Stubber(ctx.client('ecs')) as stub:
        stub_tasks(stub, {'idle': []})
        result = check('L-B7718569')(ctx)
        assert (result['usage'], result['resource_id']) == (0, cluster_arn('idle'))
        stub.assert_no_pending_responses()


def test_a_task_without_a_status_is_reported():
    ctx = context('L-B7718569')
    with Stubber(ctx.client('ecs')) as stub:
        stub.add_response('list_clusters', {'clusterArns': [cluster_arn('odd')]}, {})
        stub.add_response('list_tasks', {'taskArns': [task_arn('odd', 'a')]},
                          {'cluster': cluster_arn('odd'), 'desiredStatus': 'RUNNING'})
        stub.add_response('describe_tasks',
                          {'tasks': [{'taskArn': task_arn('odd', 'a')}]},
                          {'cluster': cluster_arn('odd'),
                           'tasks': [task_arn('odd', 'a')]})
        with pytest.raises(NoData, match='status'):
            check('L-B7718569')(ctx)
