from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import (aco_automation, aidevops, controltower,
                              migrationhubstrategy, mwaa_serverless,
                              observabilityadmin, s3_outposts, securityagent,
                              snow_device_management)
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
NOW = datetime(2026, 9, 15, tzinfo=UTC)
WORKFLOW = f'arn:aws:airflow:eu-central-1:{ACCOUNT}:workflow/etl'
OTHER_WORKFLOW = f'arn:aws:airflow:eu-central-1:{ACCOUNT}:workflow/reports'
SPACE = 'as-00000000000000001'
VERSION = '1' * 32
VERSION_TWO = '2' * 32


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 50}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def workflow(arn, name):
    return {'WorkflowArn': arn, 'Name': name, 'WorkflowStatus': 'AVAILABLE',
            'CreatedAt': NOW, 'ModifiedAt': NOW, 'WorkflowVersion': VERSION}


def test_serverless_workflows_and_versions_are_counted():
    ctx = context('airflow-serverless', 'L-430BC7B5')
    with Stubber(ctx.client('mwaa-serverless')) as stub:
        stub.add_response('list_workflows', {'Workflows': [
            workflow(WORKFLOW, 'etl'), workflow(OTHER_WORKFLOW, 'reports')]}, {})
        stub.add_response('list_workflow_versions', {'WorkflowVersions': [
            {'WorkflowVersion': VERSION, 'WorkflowArn': WORKFLOW}]},
            {'WorkflowArn': WORKFLOW})
        stub.add_response('list_workflow_versions', {'WorkflowVersions': [
            {'WorkflowVersion': VERSION, 'WorkflowArn': OTHER_WORKFLOW},
            {'WorkflowVersion': VERSION_TWO, 'WorkflowArn': OTHER_WORKFLOW}]},
            {'WorkflowArn': OTHER_WORKFLOW})
        result = mwaa_serverless.versions_per_workflow(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'reports')
        stub.assert_no_pending_responses()


def test_only_unfinished_workflow_runs_are_concurrent():
    ctx = context('airflow-serverless', 'L-643FB251')
    with Stubber(ctx.client('mwaa-serverless')) as stub:
        stub.add_response('list_workflows', {'Workflows': [workflow(WORKFLOW, 'etl')]}, {})
        stub.add_response('list_workflow_runs', {'WorkflowRuns': [
            {'RunId': 'r1', 'WorkflowArn': WORKFLOW,
             'RunDetailSummary': {'Status': 'RUNNING'}},
            {'RunId': 'r2', 'WorkflowArn': WORKFLOW,
             'RunDetailSummary': {'Status': 'QUEUED'}},
            {'RunId': 'r3', 'WorkflowArn': WORKFLOW,
             'RunDetailSummary': {'Status': 'SUCCESS'}}]}, {'WorkflowArn': WORKFLOW})
        assert mwaa_serverless.concurrent_runs(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_migration_imports_and_servers_are_counted():
    ctx = context('migrationhubstrategy', 'L-33C4B34A')
    with Stubber(ctx.client('migrationhubstrategy')) as stub:
        stub.add_response('list_import_file_task', {'taskInfos': [
            {'id': 't1', 'status': 'ImportInProgress'},
            {'id': 't2', 'status': 'DeleteInProgress'},
            {'id': 't3', 'status': 'ImportSuccess'}]}, {})
        assert migrationhubstrategy.active_imports(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
    ctx = context('migrationhubstrategy', 'L-649F667C')
    with Stubber(ctx.client('migrationhubstrategy')) as stub:
        stub.add_response('list_servers', {'serverInfos': [
            {'id': 's1'}, {'id': 's2'}, {'id': 's1'}]}, {})
        assert migrationhubstrategy.servers_per_assessment(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_unknown_import_status_raises_nodata():
    ctx = context('migrationhubstrategy', 'L-33C4B34A')
    with Stubber(ctx.client('migrationhubstrategy')) as stub:
        stub.add_response('list_import_file_task', {'taskInfos': [
            {'id': 't1', 'status': 'ImportPondering'}]}, {})
        with pytest.raises(NoData, match='unknown status'):
            migrationhubstrategy.active_imports(ctx)


def test_security_agent_jobs_are_counted_across_spaces_and_work_items():
    ctx = context('securityagent', 'L-EC8BA326')
    with Stubber(ctx.client('securityagent')) as stub:
        stub.add_response('list_agent_spaces', {'agentSpaceSummaries': [
            {'agentSpaceId': SPACE, 'name': 'main'}]}, {})
        stub.add_response('list_code_reviews', {'codeReviewSummaries': [
            {'codeReviewId': 'cr-1', 'agentSpaceId': SPACE, 'title': 'one'},
            {'codeReviewId': 'cr-2', 'agentSpaceId': SPACE, 'title': 'two'}]},
            {'agentSpaceId': SPACE})
        stub.add_response('list_code_review_jobs_for_code_review',
                          {'codeReviewJobSummaries': [
                              {'codeReviewJobId': 'j1', 'codeReviewId': 'cr-1',
                               'status': 'IN_PROGRESS'},
                              {'codeReviewJobId': 'j2', 'codeReviewId': 'cr-1',
                               'status': 'COMPLETED'}]},
                          {'agentSpaceId': SPACE, 'codeReviewId': 'cr-1'})
        stub.add_response('list_code_review_jobs_for_code_review',
                          {'codeReviewJobSummaries': [
                              {'codeReviewJobId': 'j3', 'codeReviewId': 'cr-2',
                               'status': 'STOPPING'}]},
                          {'agentSpaceId': SPACE, 'codeReviewId': 'cr-2'})
        assert check(securityagent, 'L-EC8BA326')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_snow_device_tasks_separate_total_from_active():
    tasks = [{'taskId': 't1', 'state': 'IN_PROGRESS'},
             {'taskId': 't2', 'state': 'COMPLETED'},
             {'taskId': 't3', 'state': 'CANCELED'}]
    for code, expected in (('L-D88A1E78', 3), ('L-FFEB0409', 1)):
        ctx = context('snow-device-management', code)
        with Stubber(ctx.client('snow-device-management')) as stub:
            stub.add_response('list_tasks', {'tasks': tasks}, {})
            assert check(snow_device_management, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_only_running_automation_events_are_counted():
    ctx = context('aco-automation', 'L-E486B777')
    with Stubber(ctx.client('compute-optimizer-automation')) as stub:
        stub.add_response('list_automation_events', {'automationEvents': [
            {'eventId': 'e1', 'eventStatus': 'InProgress'},
            {'eventId': 'e2', 'eventStatus': 'RollbackInProgress'},
            {'eventId': 'e3', 'eventStatus': 'Complete'},
            {'eventId': 'e4', 'eventStatus': 'Ready'}]}, {})
        assert aco_automation.executing_events(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_devops_agent_spaces_are_counted_once():
    ctx = context('aidevops', 'L-510AF4A9')
    with Stubber(ctx.client('devops-agent')) as stub:
        stub.add_response('list_agent_spaces', {'agentSpaces': [
            {'agentSpaceId': 'a1', 'name': 'one', 'createdAt': NOW,
             'updatedAt': NOW},
            {'agentSpaceId': 'a2', 'name': 'two', 'createdAt': NOW,
             'updatedAt': NOW},
            {'agentSpaceId': 'a1', 'name': 'one', 'createdAt': NOW,
             'updatedAt': NOW}]}, {})
        assert check(aidevops, 'L-510AF4A9')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_centralization_rules_are_counted_by_name():
    ctx = context('observabilityadmin', 'L-B8EC8109')
    with Stubber(ctx.client('observabilityadmin')) as stub:
        stub.add_response('list_centralization_rules_for_organization',
                          {'CentralizationRuleSummaries': [
                              {'RuleName': 'logs'}, {'RuleName': 'metrics'}]}, {})
        assert observabilityadmin.organization_centralization_rules(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_accounts_are_counted_per_organizational_unit():
    ctx = context('controltower', 'L-E9464183')
    with Stubber(ctx.client('organizations')) as stub:
        stub.add_response('list_roots', {'Roots': [{'Id': 'r-1234', 'Name': 'Root'}]}, {})
        stub.add_response('list_organizational_units_for_parent',
                          {'OrganizationalUnits': [{'Id': 'ou-1234-11111111',
                                                    'Name': 'workloads'}]},
                          {'ParentId': 'r-1234'})
        stub.add_response('list_organizational_units_for_parent',
                          {'OrganizationalUnits': []},
                          {'ParentId': 'ou-1234-11111111'})
        stub.add_response('list_accounts_for_parent', {'Accounts': [
            {'Id': '111111111111'}, {'Id': '222222222222'}]},
            {'ParentId': 'ou-1234-11111111'})
        result = controltower.accounts_per_organizational_unit(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'ou-1234-11111111')
        stub.assert_no_pending_responses()


def test_outpost_buckets_and_access_points_are_counted_per_outpost():
    outpost = 'op-0123456789abcdef0'
    bucket_arn = (f'arn:aws:s3-outposts:eu-central-1:{ACCOUNT}:outpost/{outpost}'
                  '/bucket/data')
    ctx = context('s3-outposts', 'L-C39AA790')
    outposts_stub = Stubber(ctx.client('outposts'))
    control_stub = Stubber(ctx.client('s3control'))
    with outposts_stub as ops, control_stub as control:
        ops.add_response('list_outposts', {'Outposts': [{'OutpostId': outpost}]}, {})
        control.add_response('list_regional_buckets', {'RegionalBucketList': [
            {'Bucket': 'data', 'BucketArn': bucket_arn, 'PublicAccessBlockEnabled': True,
             'CreationDate': NOW, 'OutpostId': outpost}]},
            {'AccountId': ACCOUNT, 'OutpostId': outpost})
        control.add_response('list_access_points', {'AccessPointList': [
            {'Name': 'ap-1', 'NetworkOrigin': 'Vpc', 'Bucket': 'data'},
            {'Name': 'ap-2', 'NetworkOrigin': 'Vpc', 'Bucket': 'data'}]},
            {'AccountId': ACCOUNT, 'Bucket': bucket_arn})
        result = s3_outposts.access_points_per_outpost(ctx)
        assert (result['usage'], result['resource_id']) == (2, outpost)
        ops.assert_no_pending_responses()
        control.assert_no_pending_responses()


def test_every_new_check_is_registered_for_reporting():
    for module, service in (
            (mwaa_serverless, 'airflow-serverless'),
            (migrationhubstrategy, 'migrationhubstrategy'),
            (securityagent, 'securityagent'),
            (snow_device_management, 'snow-device-management'),
            (aco_automation, 'aco-automation'), (aidevops, 'aidevops'),
            (observabilityadmin, 'observabilityadmin'),
            (controltower, 'controltower'), (s3_outposts, 's3-outposts')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service


def test_support_permits_are_counted_once():
    from modules.qmchecks import supportauthz
    ctx = context('supportauthz', 'L-EDDA9F00')
    with Stubber(ctx.client('supportauthz')) as stub:
        permit = {'name': 'p1', 'status': 'ACTIVE', 'createdAt': NOW,
                  'permit': {'actions': {'actions': ['support:DescribeCases']},
                             'resources': {'allResourcesInRegion': {}}},
                  'signingKeyInfo': {'kmsKey': 'arn:aws:kms:eu-central-1:'
                                               '123456789012:key/abcd'}}
        stub.add_response('list_support_permits', {'supportPermits': [
            dict(permit, arn='arn:aws:supportauthz::123456789012:permit/p1'),
            dict(permit, arn='arn:aws:supportauthz::123456789012:permit/p2'),
            dict(permit, arn='arn:aws:supportauthz::123456789012:permit/p1')]}, {})
        assert supportauthz.support_permits(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
