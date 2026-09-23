"""Provisioned throughput units and Bedrock's concurrent job inventories."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import bedrock_throughput as throughput
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 15, tzinfo=UTC)
BASE = 'arn:aws:bedrock:eu-central-1::foundation-model/amazon.nova-lite-v1:0'
CUSTOM = 'arn:aws:bedrock:eu-central-1:123456789012:custom-model/mine'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in throughput.CHECKS if quota == code)


def provisioned(name, model_arn, units, commitment=None):
    summary = {'provisionedModelName': name, 'provisionedModelArn': f'arn:pm/{name}',
               'modelArn': model_arn, 'desiredModelArn': model_arn,
               'foundationModelArn': BASE, 'modelUnits': units, 'desiredModelUnits': units,
               'status': 'InService', 'creationTime': MOMENT, 'lastModifiedTime': MOMENT}
    if commitment:
        summary['commitmentDuration'] = commitment
    return summary


@pytest.mark.parametrize('code, expected', [('L-FE44174A', 3), ('L-BE77399C', 5)])
def test_only_uncommitted_units_count_and_each_model_kind_separately(code, expected):
    """A committed throughput is bought against a different quota."""
    ctx = context(code)
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_provisioned_model_throughputs', {'provisionedModelSummaries': [
            provisioned('base-free', BASE, 3),
            provisioned('base-committed', BASE, 7, commitment='OneMonth'),
            provisioned('custom-free', CUSTOM, 5)]}, {})
        assert check(code)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def test_an_unrecognised_model_arn_is_reported_rather_than_skipped():
    ctx = context('L-FE44174A')
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_provisioned_model_throughputs', {'provisionedModelSummaries': [
            provisioned('odd', 'arn:aws:bedrock:eu-central-1::imported-model/x', 1)]}, {})
        with pytest.raises(NoData, match='neither base nor custom'):
            check('L-FE44174A')(ctx)


def stub_ingestion(stub, jobs):
    stub.add_response('list_knowledge_bases', {'knowledgeBaseSummaries': [
        {'knowledgeBaseId': 'kb-1', 'name': 'one', 'status': 'ACTIVE', 'updatedAt': MOMENT},
        {'knowledgeBaseId': 'kb-2', 'name': 'two', 'status': 'ACTIVE', 'updatedAt': MOMENT}]}, {})
    for base, sources in jobs.items():
        stub.add_response('list_data_sources', {'dataSourceSummaries': [
            {'knowledgeBaseId': base, 'dataSourceId': source, 'name': source,
             'status': 'AVAILABLE', 'updatedAt': MOMENT} for source in sources]},
            {'knowledgeBaseId': base})
        for source, statuses in sources.items():
            stub.add_response('list_ingestion_jobs', {'ingestionJobSummaries': [
                {'knowledgeBaseId': base, 'dataSourceId': source, 'ingestionJobId': f'job{index}',
                 'status': status, 'startedAt': MOMENT, 'updatedAt': MOMENT}
                for index, status in enumerate(statuses)]},
                {'knowledgeBaseId': base, 'dataSourceId': source})


JOBS = {'kb-1': {'ds-1': ['IN_PROGRESS', 'COMPLETE'], 'ds-2': ['STARTING']},
        'kb-2': {'ds-3': ['STOPPING', 'FAILED', 'IN_PROGRESS']}}


def test_ingestion_jobs_count_everything_that_has_not_finished():
    """STOPPING still occupies a slot, so only the finished states are excluded."""
    ctx = context('L-795A8608')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub_ingestion(stub, JOBS)
        assert check('L-795A8608')(ctx)['usage'] == 4
        stub.assert_no_pending_responses()


def test_ingestion_jobs_per_knowledge_base_sum_their_data_sources():
    ctx = context('L-31BC8F89')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub_ingestion(stub, JOBS)
        result = check('L-31BC8F89')(ctx)
        # kb-1 runs one per data source, kb-2 runs two in a single one.
        assert (result['usage'], result['resource_id']) == (2, 'kb-1')
        stub.assert_no_pending_responses()


def test_ingestion_jobs_per_data_source_use_the_busiest_source():
    ctx = context('L-D38407FA')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub_ingestion(stub, JOBS)
        result = check('L-D38407FA')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'kb-2/ds-3')
        stub.assert_no_pending_responses()


def stub_builds(stub):
    stub.add_response('list_automated_reasoning_policies',
                      {'automatedReasoningPolicySummaries': [
                          {'policyArn': 'arn:policy/a', 'name': 'a', 'version': '1',
                           'policyId': 'a', 'createdAt': MOMENT, 'updatedAt': MOMENT},
                          {'policyArn': 'arn:policy/b', 'name': 'b', 'version': '1',
                           'policyId': 'b', 'createdAt': MOMENT, 'updatedAt': MOMENT}]}, {})
    for arn, statuses in [('arn:policy/a', ['BUILDING', 'COMPLETED']),
                          ('arn:policy/b', ['SCHEDULED', 'TESTING', 'CANCELLED'])]:
        stub.add_response('list_automated_reasoning_policy_build_workflows',
                          {'automatedReasoningPolicyBuildWorkflowSummaries': [
                              {'policyArn': arn, 'buildWorkflowId': f'w{index}', 'status': status,
                               'buildWorkflowType': 'INGEST_CONTENT',
                               'createdAt': MOMENT, 'updatedAt': MOMENT}
                              for index, status in enumerate(statuses)]},
                          {'policyArn': arn})


def test_policy_builds_count_every_workflow_still_in_flight():
    ctx = context('L-1B9EB555')
    with Stubber(ctx.client('bedrock')) as stub:
        stub_builds(stub)
        assert check('L-1B9EB555')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_builds_per_policy_use_the_busiest_policy():
    ctx = context('L-908FAEE3')
    with Stubber(ctx.client('bedrock')) as stub:
        stub_builds(stub)
        result = check('L-908FAEE3')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'arn:policy/b')
        stub.assert_no_pending_responses()
