"""Entity Resolution job concurrency and AWS Backup in-flight jobs."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import backup, entityresolution
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=timezone.utc)


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def workflow(name, resolution=None):
    entry = {'workflowName': name, 'workflowArn': f'arn:wf/{name}',
             'createdAt': MOMENT, 'updatedAt': MOMENT}
    if resolution:
        entry['resolutionType'] = resolution
    return entry


def job(job_id, status):
    return {'jobId': job_id, 'status': status, 'startTime': MOMENT}


def test_matching_jobs_count_only_the_running_ones_across_workflows():
    """A queued job is waiting for the quota, so counting it would double it."""
    ctx = context('entityresolution', 'L-6FC8FD6D')
    with Stubber(ctx.client('entityresolution')) as stub:
        stub.add_response('list_matching_workflows', {'workflowSummaries': [
            workflow('one', 'RULE_MATCHING'), workflow('two', 'ML_MATCHING')]}, {})
        stub.add_response('list_matching_jobs', {'jobs': [
            job('j1', 'RUNNING'), job('j2', 'QUEUED'), job('j3', 'SUCCEEDED')]},
            {'workflowName': 'one'})
        stub.add_response('list_matching_jobs', {'jobs': [job('j4', 'RUNNING')]},
                          {'workflowName': 'two'})
        result = check('L-6FC8FD6D', entityresolution.CHECKS)(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_SUM')
        stub.assert_no_pending_responses()


def test_an_unknown_job_status_is_reported_rather_than_assumed_idle():
    ctx = context('entityresolution', 'L-6FC8FD6D')
    with Stubber(ctx.client('entityresolution')) as stub:
        stub.add_response('list_matching_workflows',
                          {'workflowSummaries': [workflow('one', 'RULE_MATCHING')]}, {})
        stub.add_response('list_matching_jobs', {'jobs': [job('j1', 'PONDERING')]},
                          {'workflowName': 'one'})
        with pytest.raises(NoData, match='status'):
            check('L-6FC8FD6D', entityresolution.CHECKS)(ctx)


@pytest.mark.parametrize('code, expected', [
    ('L-0A2F654F', 3),   # every ID mapping workflow
    ('L-06117805', 1),   # only the provider-service matching workflows
])
def test_provider_service_jobs_are_told_apart_by_the_resolution_type(code, expected):
    """The listing states the resolution type, so no workflow detail is read."""
    ctx = context('entityresolution', code)
    with Stubber(ctx.client('entityresolution')) as stub:
        if code == 'L-06117805':
            stub.add_response('list_matching_workflows', {'workflowSummaries': [
                workflow('rules', 'RULE_MATCHING'), workflow('provider', 'PROVIDER')]}, {})
            stub.add_response('list_matching_jobs', {'jobs': [job('j3', 'RUNNING')]},
                              {'workflowName': 'provider'})
        else:
            stub.add_response('list_id_mapping_workflows',
                              {'workflowSummaries': [workflow('rules'), workflow('provider')]}, {})
            stub.add_response('list_id_mapping_jobs',
                              {'jobs': [job('j1', 'RUNNING'), job('j2', 'RUNNING')]},
                              {'workflowName': 'rules'})
            stub.add_response('list_id_mapping_jobs', {'jobs': [job('j3', 'RUNNING')]},
                              {'workflowName': 'provider'})
        assert check(code, entityresolution.CHECKS)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def backup_job(job_id, resource, state):
    return {'BackupJobId': job_id, 'ResourceArn': resource, 'State': state,
            'ResourceType': 'EBS', 'CreationDate': MOMENT, 'AccountId': '123456789012'}


def test_backup_jobs_are_counted_per_resource_and_only_while_in_flight():
    """AWS filters by one state at a time, so each unfinished state is asked for."""
    ctx = context('backup', 'L-366B61FD')
    with Stubber(ctx.client('backup')) as stub:
        for state, jobs in (('CREATED', [backup_job('b1', 'arn:vol/a', 'CREATED')]),
                            ('PENDING', []),
                            ('RUNNING', [backup_job('b2', 'arn:vol/a', 'RUNNING'),
                                         backup_job('b3', 'arn:vol/b', 'RUNNING')])):
            stub.add_response('list_backup_jobs', {'BackupJobs': jobs}, {'ByState': state})
        result = check('L-366B61FD', backup.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'arn:vol/a')
        stub.assert_no_pending_responses()


def test_copy_jobs_are_counted_per_service_not_per_resource():
    ctx = context('backup', 'L-FFD6444F')
    with Stubber(ctx.client('backup')) as stub:
        stub.add_response('list_copy_jobs', {'CopyJobs': [
            {'CopyJobId': 'c1', 'ResourceType': 'EBS', 'State': 'CREATED',
             'CreationDate': MOMENT}]}, {'ByState': 'CREATED'})
        stub.add_response('list_copy_jobs', {'CopyJobs': [
            {'CopyJobId': 'c2', 'ResourceType': 'EBS', 'State': 'RUNNING',
             'CreationDate': MOMENT},
            {'CopyJobId': 'c3', 'ResourceType': 'RDS', 'State': 'RUNNING',
             'CreationDate': MOMENT}]}, {'ByState': 'RUNNING'})
        result = check('L-FFD6444F', backup.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'EBS')
        stub.assert_no_pending_responses()


def test_a_backup_job_without_its_resource_is_reported():
    ctx = context('backup', 'L-366B61FD')
    with Stubber(ctx.client('backup')) as stub:
        stub.add_response('list_backup_jobs', {'BackupJobs': [
            {'BackupJobId': 'b1', 'State': 'CREATED', 'CreationDate': MOMENT}]},
            {'ByState': 'CREATED'})
        with pytest.raises(NoData, match='resource'):
            check('L-366B61FD', backup.CHECKS)(ctx)
