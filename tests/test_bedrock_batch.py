from datetime import datetime, UTC
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.bedrock import CHECKS as ORIGINAL, get_current_quotastatus_bedrock
from modules.qmchecks.bedrock_batch import CHECKS, MODEL_QUOTAS, batch_jobs, resolve_model
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

MODEL = 'amazon.titan-embed-image-v1'
OTHER = 'amazon.nova-lite-v1:0'
BASE_CODE, CUSTOM_CODE = 'L-7F2C6F33', 'L-652C224A'
NOW = datetime(2026, 9, 11, tzinfo=UTC)
CUSTOM_ARN = 'arn:aws:bedrock:eu-central-1:123456789012:custom-model/custom/123456789012'


def foundation(model=MODEL, region='eu-central-1'):
    return f'arn:aws:bedrock:{region}::foundation-model/{model}'


def job(name, model=MODEL, status='InProgress'):
    return dict(jobArn=f'arn:aws:bedrock:eu-central-1:123456789012:model-invocation-job/{name}',
                jobName=name, modelId=model, status=status, submitTime=NOW,
                roleArn='arn:aws:iam::123456789012:role/batch',
                inputDataConfig={'s3InputDataConfig': {'s3Uri': 's3://input-bucket/jobs/'}},
                outputDataConfig={'s3OutputDataConfig': {'s3Uri': 's3://output-bucket/jobs/'}})


def context():
    return CheckContext(boto3.Session(region_name='eu-central-1'), [
        {'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}
        for code in [BASE_CODE, CUSTOM_CODE]], account='123456789012')


def profile(identifier, models):
    return dict(inferenceProfileName='profile', inferenceProfileArn=(identifier if identifier.startswith('arn:') else
                f'arn:aws:bedrock:eu-central-1:123456789012:inference-profile/{identifier}'),
                inferenceProfileId=identifier.split('/')[-1], status='ACTIVE', type='SYSTEM_DEFINED',
                models=[{'modelArn': model} for model in models])


def test_jobs_paginate_deduplicate_and_separate_base_from_custom_models():
    ctx = context()
    first = job('first', status='Submitted')
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_model_invocation_jobs', {'invocationJobSummaries': [first, job('completed', status='Completed')],
                                                       'nextToken': 'next'}, {})
        stub.add_response('list_model_invocation_jobs', {'invocationJobSummaries': [
            first, job('foundation', foundation()), job('custom', CUSTOM_ARN), job('other', OTHER)]}, {'nextToken': 'next'})
        stub.add_response('get_custom_model', {'modelArn': CUSTOM_ARN, 'modelName': 'custom',
                          'creationTime': NOW, 'baseModelArn': foundation()}, {'modelIdentifier': CUSTOM_ARN})
        results = get_current_quotastatus_bedrock(ctx=ctx, skip={('bedrock', code) for code, _, _ in ORIGINAL})
        assert [(r['quotaCode'], r['usageValue'], r['qualityStatus']) for r in results] == [
            (CUSTOM_CODE, 1, 'OK'), (BASE_CODE, 2, 'OK')]
        stub.assert_no_pending_responses()  # Shared inventory and model resolution are cached.


@pytest.mark.parametrize('identifier', ['eu.amazon.nova-lite-v1:0', 'application123',
    'arn:aws:bedrock:eu-central-1:123456789012:application-inference-profile/application123'])
def test_cross_region_and_application_profiles_resolve_without_multiplying_jobs(identifier):
    ctx = context()
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_model_invocation_jobs', {'invocationJobSummaries': [job('profile-job', identifier)]}, {})
        stub.add_response('get_inference_profile', profile(identifier, [foundation(OTHER), foundation(OTHER, 'eu-west-1')]),
                          {'inferenceProfileIdentifier': identifier})
        assert batch_jobs(ctx, OTHER, 'base')['usage'] == 1
        assert batch_jobs(ctx, MODEL, 'base')['usage'] == 0
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('status', ['Validating', 'Scheduled', 'Stopping', 'Unknown', None])
def test_ambiguous_states_do_not_return_a_partial_count(status):
    ctx = Mock()
    ctx.call.return_value = [job('counted'), job('unknown', status=status)]
    with pytest.raises(NoData):
        batch_jobs(ctx, MODEL, 'base')


@pytest.mark.parametrize('status', ['Completed', 'PartiallyCompleted', 'Failed', 'Stopped', 'Expired'])
def test_terminal_jobs_do_not_require_still_existing_model_metadata(status):
    ctx = Mock()
    ctx.call.return_value = [job('finished', 'arn:aws:bedrock:eu-central-1:123456789012:custom-model/deleted/id', status)]
    assert batch_jobs(ctx, MODEL, 'base')['usage'] == 0
    assert ctx.call.call_count == 1


def test_ambiguous_state_on_verified_unrelated_model_does_not_block_target():
    ctx = Mock()
    ctx.call.return_value = [job('other', OTHER, 'Validating'), job('target')]
    assert batch_jobs(ctx, MODEL, 'base')['usage'] == 1


def test_conflicting_duplicate_job_is_unknown():
    ctx = Mock()
    ctx.call.return_value = [job('same'), job('same', status='Completed')]
    with pytest.raises(NoData, match='changed'):
        batch_jobs(ctx, MODEL, 'base')


@pytest.mark.parametrize('models', [[], [foundation(), foundation(OTHER)]])
def test_profiles_without_one_unambiguous_base_model_are_unknown(models):
    ctx = Mock()
    ctx.call.return_value = profile('eu.model', models)
    with pytest.raises(NoData):
        resolve_model(ctx, 'eu.model')


def test_unknown_direct_model_is_verified_via_aws_before_excluding_it():
    ctx = context()
    other = 'amazon.another-model-v1:0'
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_model_invocation_jobs', {'invocationJobSummaries': [job('other', other)]}, {})
        stub.add_response('get_foundation_model', {'modelDetails': {'modelId': other, 'modelArn': foundation(other)}},
                          {'modelIdentifier': other})
        assert batch_jobs(ctx, MODEL, 'base')['usage'] == 0
        stub.assert_no_pending_responses()


def test_failed_later_page_returns_error_without_partial_usage():
    ctx = context()
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_model_invocation_jobs', {'invocationJobSummaries': [job('one')], 'nextToken': 'next'}, {})
        stub.add_client_error('list_model_invocation_jobs', 'AccessDeniedException', expected_params={'nextToken': 'next'})
        results = get_current_quotastatus_bedrock(ctx=ctx, skip={('bedrock', code) for code, _, _ in ORIGINAL})
        assert all(row['qualityStatus'] == 'ERROR' and row['usageValue'] is None for row in results)


def test_batch_quota_registration_is_unique_and_available_to_collector():
    keys = custom_keys()
    # A model may hold two codes, because the two exports issue it twice; a
    # code mapped twice would be the bug. The count itself is not an invariant.
    codes = [code for code, _model, _kind in MODEL_QUOTAS]
    assert len(set(codes)) == len(codes), 'a batch model quota code is mapped twice'
    assert all(('bedrock', code) in keys for code, _, _ in CHECKS)
