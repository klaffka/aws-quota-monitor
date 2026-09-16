"""ECS cluster/service scopes and IoT TwinMaker workspace inventories."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ecs, twinmaker
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 15, tzinfo=timezone.utc)
CLUSTER = 'arn:aws:ecs:eu-central-1:123456789012:cluster/one'
SERVICES = [f'arn:aws:ecs:eu-central-1:123456789012:service/one/s{index}' for index in range(12)]


def context(service, code, client):
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                       account='123456789012')
    return ctx, Stubber(ctx.client(client))


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def test_capacity_providers_use_the_largest_cluster():
    ctx, stub = context('ecs', 'L-A24B7D58', 'ecs')
    with stub:
        stub.add_response('list_clusters', {'clusterArns': [CLUSTER]}, {})
        stub.add_response('describe_clusters', {'clusters': [
            {'clusterArn': CLUSTER, 'clusterName': 'one',
             'capacityProviders': ['FARGATE', 'FARGATE_SPOT']}]}, {'clusters': [CLUSTER]})
        result = check(ecs, 'L-A24B7D58')(ctx)
        assert (result['usage'], result['resource_id']) == (2, CLUSTER)
        stub.assert_no_pending_responses()


def stub_services(stub, services):
    stub.add_response('list_clusters', {'clusterArns': [CLUSTER]}, {})
    stub.add_response('list_services', {'serviceArns': SERVICES[:len(services)]},
                      {'cluster': CLUSTER})
    for start in range(0, len(services), ecs.SERVICE_BATCH):
        batch = services[start:start + ecs.SERVICE_BATCH]
        stub.add_response('describe_services', {'services': batch},
                          {'cluster': CLUSTER,
                           'services': SERVICES[start:start + len(batch)]})


def service(index, **fields):
    return {'serviceArn': SERVICES[index], 'serviceName': f's{index}',
            'clusterArn': CLUSTER, **fields}


def test_services_are_described_in_batches_of_ten():
    """DescribeServices takes at most ten, so eleven services need two calls."""
    ctx, stub = context('ecs', 'L-92E49DE3', 'ecs')
    with stub:
        services = [service(index, runningCount=index, desiredCount=0) for index in range(11)]
        stub_services(stub, services)
        result = check(ecs, 'L-92E49DE3')(ctx)
        assert (result['usage'], result['resource_id']) == (10, SERVICES[10])
        stub.assert_no_pending_responses()


def test_tasks_per_service_never_report_less_than_the_desired_count():
    """A service scaling up runs fewer tasks than the quota must accommodate."""
    ctx, stub = context('ecs', 'L-92E49DE3', 'ecs')
    with stub:
        stub_services(stub, [service(0, runningCount=2, desiredCount=7)])
        assert check(ecs, 'L-92E49DE3')(ctx)['usage'] == 7
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, field', [('L-A04A77EF', 'targetGroupArn'),
                                         ('L-E4A1E1D7', 'loadBalancerName')])
def test_each_load_balancer_quota_counts_only_its_own_kind(code, field):
    ctx, stub = context('ecs', code, 'ecs')
    with stub:
        stub_services(stub, [service(0, loadBalancers=[
            {'targetGroupArn': 'arn:tg/one'}, {'targetGroupArn': 'arn:tg/two'},
            {'loadBalancerName': 'classic'}])])
        assert check(ecs, code)(ctx)['usage'] == (2 if field == 'targetGroupArn' else 1)
        stub.assert_no_pending_responses()


WORKSPACES = {'workspaceSummaries': [
    {'workspaceId': 'ws-1', 'arn': 'arn:aws:iottwinmaker:eu-central-1:123456789012:workspace/ws-1', 'creationDateTime': MOMENT,
     'updateDateTime': MOMENT},
    {'workspaceId': 'ws-2', 'arn': 'arn:aws:iottwinmaker:eu-central-1:123456789012:workspace/ws-2', 'creationDateTime': MOMENT,
     'updateDateTime': MOMENT}]}


def test_entities_use_the_largest_workspace():
    ctx, stub = context('iottwinmaker', 'L-ADB4D9B9', 'iottwinmaker')
    with stub:
        stub.add_response('list_workspaces', WORKSPACES, {})
        stub.add_response('list_entities', {'entitySummaries': [
            {'entityId': 'e1', 'entityName': 'one', 'arn': 'arn:aws:iottwinmaker:eu-central-1:123456789012:entity/e1',
             'status': {'state': 'ACTIVE'}, 'creationDateTime': MOMENT,
             'updateDateTime': MOMENT}]}, {'workspaceId': 'ws-1'})
        stub.add_response('list_entities', {'entitySummaries': [
            {'entityId': f'e{index}', 'entityName': f'name{index}', 'arn': f'arn:aws:iottwinmaker:eu-central-1:123456789012:entity/e{index}',
             'status': {'state': 'ACTIVE'}, 'creationDateTime': MOMENT,
             'updateDateTime': MOMENT} for index in (2, 3)]}, {'workspaceId': 'ws-2'})
        result = check(twinmaker, 'L-ADB4D9B9')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'ws-2')
        stub.assert_no_pending_responses()


def test_a_workspace_without_an_identity_is_reported_as_no_data():
    """workspaceId is a required output member, so only a broken response can
    omit it; a Stubber refuses to produce one. The check must still refuse to
    report a count for a workspace it cannot name."""
    from unittest.mock import Mock

    ctx = Mock()
    ctx.call.return_value = [{'arn': 'arn:workspace'}]
    with pytest.raises(NoData, match='missing its identity'):
        check(twinmaker, 'L-8E0F7923')(ctx)
