from datetime import datetime, timezone
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import bedrock_evaluation as evaluation
from modules.qmchecks import bedrock_reasoning as reasoning
from modules.qmchecks.bedrock import ALL_CHECKS, CHECKS, blueprint_count, get_current_quotastatus_bedrock
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

NOW = datetime(2026, 9, 11, tzinfo=timezone.utc)
ARN = 'arn:aws:bedrock:eu-central-1:123456789012:automated-reasoning-policy/abcdefghijkl'
JOB = 'arn:aws:bedrock:eu-central-1:123456789012:evaluation-job/abcdefghijkl'


def context(code='L-F32E9946'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}], account='123456789012')


def summary(version='DRAFT', arn=ARN):
    return dict(policyArn=arn if version in {'DRAFT', ''} else arn+':'+version,
                policyId=arn.rsplit('/', 1)[1], version=version, name='policy', createdAt=NOW, updatedAt=NOW)


def job(kind='Automated', status='InProgress', arn=JOB):
    return dict(jobArn=arn, jobName='job', status=status, creationTime=NOW,
                jobType=kind, evaluationTaskTypes=['Generation'], applicationType='ModelEvaluation')


def detail(kind='Automated', arn=JOB):
    datasets = [{'taskType': 'Generation', 'dataset': {'name': 'Builtin'}, 'metricNames': ['Accuracy']},
                {'taskType': 'Generation', 'dataset': {'name': 'Custom', 'datasetLocation': {'s3Uri': 's3://bucket/input'}},
                 'metricNames': ['Accuracy', 'Robustness', 'Toxicity']}]
    settings = {'datasetMetricConfigs': datasets}
    if kind == 'Human':
        settings['customMetrics'] = [{'name': 'Quality', 'ratingMethod': 'LikertScale'}]
    return dict(jobArn=arn, jobName='job', status='InProgress', creationTime=NOW, jobType=kind,
                applicationType='ModelEvaluation', roleArn='arn:aws:iam::123456789012:role/Evaluation',
                evaluationConfig={kind.lower(): settings},
                inferenceConfig={'models': [{'bedrockModel': {'modelIdentifier': 'amazon.nova-lite-v1:0'}}]
                                 + ([{'precomputedInferenceSource': {'inferenceSourceIdentifier': 'other-model'}}]
                                    if kind == 'Human' else [])},
                outputDataConfig={'s3Uri': 's3://bucket/output'})


def test_policy_definitions_include_all_versions_paginate_and_cache_exports():
    ctx = context()
    definition = {'version': '1.0', 'types': [{'name': 'PRIVATE_TYPE', 'values': [{'value': str(i)} for i in range(3)]}],
                  'rules': [{'id': 'rule12345678', 'expression': 'PRIVATE_RULE'}],
                  'variables': [{'name': 'v1', 'type': 'Bool', 'description': 'PRIVATE_TEXT'}]}
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_automated_reasoning_policies',
                          {'automatedReasoningPolicySummaries': [summary()]}, {})
        stub.add_response('list_automated_reasoning_policies',
                          {'automatedReasoningPolicySummaries': [summary(), summary('1')], 'nextToken': 'next'},
                          {'policyArn': ARN})
        stub.add_response('list_automated_reasoning_policies',
                          {'automatedReasoningPolicySummaries': [summary('1'), summary('2')]},
                          {'policyArn': ARN, 'nextToken': 'next'})
        for target, data in [(ARN, {}), (ARN+':1', definition), (ARN+':2', {'types': []})]:
            stub.add_response('export_automated_reasoning_policy_version', {'policyDefinition': data}, {'policyArn': target})
        result = reasoning.configuration(ctx, 'types')
        assert (result['usage'], result['resource_id']) == (1, ARN+':1')
        assert reasoning.configuration(ctx, 'types', per_type=True)['usage'] == 3
        assert reasoning.configuration(ctx, 'variables')['usage'] == 1
        assert reasoning.configuration(ctx, 'rules')['usage'] == 1
        assert reasoning.version_count(ctx)['usage'] == 2
        assert 'PRIVATE' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('item', [summary('0'), dict(summary('1'), version='2'),
                                  dict(summary(), policyId='other'), dict(summary(), version=None)])
def test_policy_identity_rejects_inconsistent_versions(item):
    with pytest.raises(NoData):
        reasoning.policy_identity(item)


def test_empty_version_is_draft_and_wrong_parent_is_rejected():
    assert reasoning.policy_identity(summary('')) == (ARN, 'DRAFT')
    ctx = Mock()
    ctx.call.return_value = [summary('1', ARN.replace('abcdefghijkl', 'mnopqrstuvwx'))]
    with pytest.raises(NoData):
        reasoning.policy_versions(ctx, ARN)


@pytest.mark.parametrize('definition', [None, {'types': None}, {'types': [{}]}])
def test_missing_policy_definition_or_type_values_is_not_zero(definition):
    ctx = Mock()
    ctx.call.side_effect = [[summary()], [], {'policyDefinition': definition}]
    with pytest.raises(NoData):
        reasoning.configuration(ctx, 'types', per_type=True)


def test_policy_tests_are_counted_per_policy_and_paginated_without_content_metadata():
    ctx = context('L-54C7BE29')
    test_case = dict(testCaseId='test-1', guardContent='PRIVATE_CONTENT', createdAt=NOW, updatedAt=NOW)
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_automated_reasoning_policies', {'automatedReasoningPolicySummaries': [summary()]}, {})
        stub.add_response('list_automated_reasoning_policy_test_cases', {'testCases': [test_case], 'nextToken': 'next'}, {'policyArn': ARN})
        stub.add_response('list_automated_reasoning_policy_test_cases',
                          {'testCases': [test_case, dict(test_case, testCaseId='test-2')]}, {'policyArn': ARN, 'nextToken': 'next'})
        result = reasoning.test_count(ctx)
        assert (result['usage'], result['resource_id']) == (2, ARN)
        assert 'PRIVATE' not in str(result)
        stub.assert_no_pending_responses()


def test_later_policy_export_failure_prevents_partial_collector_result():
    ctx = context()
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_automated_reasoning_policies', {'automatedReasoningPolicySummaries': [summary()]}, {})
        stub.add_response('list_automated_reasoning_policies', {'automatedReasoningPolicySummaries': [summary('1')]}, {'policyArn': ARN})
        stub.add_response('export_automated_reasoning_policy_version', {'policyDefinition': {}}, {'policyArn': ARN})
        stub.add_client_error('export_automated_reasoning_policy_version', 'AccessDeniedException', expected_params={'policyArn': ARN+':1'})
        row, = get_current_quotastatus_bedrock(ctx=ctx, skip={('bedrock', code) for code, _, _ in CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None


def test_evaluation_pagination_scopes_types_and_reuses_details_for_all_configuration_checks():
    ctx = context()
    human = JOB[:-1]+'m'
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_evaluation_jobs', {'jobSummaries': [job(), job('Human', arn=human)], 'nextToken': 'next'},
                          {'applicationTypeEquals': 'ModelEvaluation'})
        stub.add_response('list_evaluation_jobs', {'jobSummaries': [job()]},
                          {'applicationTypeEquals': 'ModelEvaluation', 'nextToken': 'next'})
        stub.add_response('get_evaluation_job', detail(), {'jobIdentifier': JOB})
        stub.add_response('get_evaluation_job', detail('Human', human), {'jobIdentifier': human})
        assert evaluation.evaluation_count(ctx)['usage'] == 2
        assert evaluation.evaluation_count(ctx, 'Automated')['usage'] == 1
        assert evaluation.evaluation_count(ctx, 'Human')['usage'] == 1
        for measure, expected in [('models', 1), ('datasets', 2), ('metrics', 3)]:
            assert evaluation.evaluation_configuration(ctx, 'Automated', measure)['usage'] == expected
        for measure, expected in [('models', 2), ('customMetrics', 1), ('customDatasets', 1)]:
            result = evaluation.evaluation_configuration(ctx, 'Human', measure)
            assert result['usage'] == expected
            assert 's3://' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('status', ['Stopping', 'Deleting', 'Unknown', None])
def test_unresolved_evaluation_reservations_are_unknown_only_for_affected_job_type(status):
    ctx = Mock()
    ctx.call.return_value = [job('Human', status)]
    with pytest.raises(NoData):
        evaluation.evaluation_count(ctx, 'Human')
    assert evaluation.evaluation_count(ctx, 'Automated')['usage'] == 0


def test_evaluation_terminal_jobs_remain_in_inventory_but_not_concurrency():
    ctx = Mock()
    ctx.call.return_value = [job(status=status, arn=JOB+str(i)) for i, status in enumerate(['Completed', 'Failed', 'Stopped'])]
    assert evaluation.evaluation_count(ctx)['usage'] == 3
    assert evaluation.evaluation_count(ctx, 'Automated')['usage'] == 0


@pytest.mark.parametrize('changes', [{'jobArn': JOB+'other'}, {'jobType': 'Human'},
                                     {'applicationType': 'RagEvaluation'}, {'evaluationConfig': {}},
                                     {'inferenceConfig': {'ragConfigs': []}}])
def test_inconsistent_evaluation_details_do_not_produce_measurements(changes):
    ctx = Mock()
    ctx.call.side_effect = [[job()], dict(detail(), **changes)]
    with pytest.raises(NoData):
        evaluation.evaluation_configuration(ctx, 'Automated', 'models')


def test_evaluation_unknown_scope_and_conflicting_pages_are_rejected():
    ctx = Mock()
    ctx.call.return_value = [dict(job(), applicationType='RagEvaluation')]
    with pytest.raises(NoData):
        evaluation.evaluation_count(ctx)
    ctx.call.return_value = [job(), job(status='Completed')]
    with pytest.raises(NoData):
        evaluation.evaluation_count(ctx)


def test_evaluation_missing_datasets_is_no_data_through_collector():
    ctx = context('L-FD0CC292')
    data = detail()
    data['evaluationConfig']['automated'].pop('datasetMetricConfigs')
    ctx.call = Mock(side_effect=[[job()], data])
    row, = get_current_quotastatus_bedrock(ctx=ctx, skip={('bedrock', code) for code, _, _ in CHECKS})
    assert row['qualityStatus'] == 'NO_DATA'
    assert row['usageValue'] is None


def test_import_jobs_paginate_deduplicate_and_exclude_finished_jobs():
    ctx = context('L-5F098EFA')
    active = dict(jobArn=JOB.replace('evaluation-job', 'model-import-job'), jobName='import', status='InProgress', creationTime=NOW)
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_model_import_jobs', {'modelImportJobSummaries': [active], 'nextToken': 'next'}, {})
        stub.add_response('list_model_import_jobs', {'modelImportJobSummaries': [active, dict(active, jobArn=active['jobArn']+'m', status='Completed')]}, {'nextToken': 'next'})
        assert evaluation.import_jobs(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_unknown_import_state_is_not_zero_and_empty_inventory_is_zero():
    ctx = Mock()
    ctx.call.return_value = [{'jobArn': JOB, 'status': 'Unknown'}]
    with pytest.raises(NoData):
        evaluation.import_jobs(ctx)
    ctx.call.return_value = []
    assert evaluation.import_jobs(ctx)['usage'] == 0
    assert reasoning.configuration(ctx, 'rules')['usage'] == 0


def test_blueprints_include_development_and_live_without_counting_stages_twice():
    ctx = context('L-23CF4444')
    arn = 'arn:aws:bedrock:eu-central-1:123456789012:blueprint/abcdefghijkl'
    params = dict(resourceOwner='ACCOUNT', blueprintStageFilter='ALL')
    with Stubber(ctx.client('bedrock-data-automation')) as stub:
        stub.add_response('list_blueprints', {'blueprints': [{'blueprintArn': arn, 'blueprintStage': 'LIVE', 'creationTime': NOW}], 'nextToken': 'next'}, params)
        stub.add_response('list_blueprints', {'blueprints': [{'blueprintArn': arn, 'blueprintStage': 'DEVELOPMENT', 'creationTime': NOW},
                                                           {'blueprintArn': arn[:-1]+'m', 'blueprintStage': 'DEVELOPMENT', 'creationTime': NOW}]},
                          dict(params, nextToken='next'))
        assert blueprint_count(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_blueprint_without_identity_is_no_data():
    ctx = Mock()
    ctx.call.return_value = [{}]
    with pytest.raises(NoData):
        blueprint_count(ctx)


def test_new_checks_are_registered_and_have_required_iam_permissions():
    new = reasoning.CHECKS + evaluation.CHECKS
    assert len(new) == len({code for code, _, _ in new}) == 16
    assert {('bedrock', code) for code, _, _ in new} <= custom_keys()
    assert len(ALL_CHECKS) == len({code for code, _, _ in ALL_CHECKS})
    for action in ['ExportAutomatedReasoningPolicyVersion', 'ListAutomatedReasoningPolicyTestCases',
                   'ListEvaluationJobs', 'GetEvaluationJob', 'ListModelImportJobs']:
        assert grants(f'bedrock:{action}')
