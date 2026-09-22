from datetime import datetime, timezone
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import rekognition as checks
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

PROJECT = 'arn:aws:rekognition:eu-central-1:123456789012:project/example/1234567890'
VIDEO = 'arn:aws:kinesisvideo:eu-central-1:123456789012:stream/video/1234567890'
OUTPUT = 'arn:aws:kinesis:eu-central-1:123456789012:stream/output'
NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)


def context(code='L-5E225387'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'rekognition', 'QuotaCode': code, 'Value': 10}], account='123456789012')


def version(name='one', status='RUNNING', project=PROJECT, **values):
    return {'ProjectVersionArn': project.rsplit('/', 1)[0] + f'/version/{name}/1234567890',
            'Feature': 'CUSTOM_LABELS', 'Status': status, **values}


def processor(name='face', kind='FaceSearch', status='RUNNING', video=VIDEO):
    return {'Name': name, 'Status': status, 'Settings': {kind: {'CollectionId': 'collection'} if kind == 'FaceSearch' else {'Labels': ['PERSON']}},
            'Input': {'KinesisVideoStream': {'Arn': video}},
            'Output': {'KinesisDataStream': {'Arn': OUTPUT}} if kind == 'FaceSearch' else {'S3Destination': {'Bucket': 'result-bucket'}}}


def test_model_inventories_filter_custom_labels_paginate_deduplicate_and_sum_projects():
    ctx = context()
    second = PROJECT.replace('example', 'another')
    with Stubber(ctx.client('rekognition')) as stub:
        stub.add_response('describe_projects', {'ProjectDescriptions': [{'ProjectArn': PROJECT}], 'NextToken': 'next'}, {'Features': ['CUSTOM_LABELS']})
        stub.add_response('describe_projects', {'ProjectDescriptions': [{'ProjectArn': second}]}, {'Features': ['CUSTOM_LABELS'], 'NextToken': 'next'})
        stub.add_response('describe_project_versions', {'ProjectVersionDescriptions': [version()], 'NextToken': 'next'}, {'ProjectArn': PROJECT})
        stub.add_response('describe_project_versions', {'ProjectVersionDescriptions': [version(), version('training', 'TRAINING_IN_PROGRESS'),
                                                                                   version('copy', 'COPYING_IN_PROGRESS')]}, {'ProjectArn': PROJECT, 'NextToken': 'next'})
        stub.add_response('describe_project_versions', {'ProjectVersionDescriptions': [version(project=second), version('finished', 'TRAINING_COMPLETED', second)]}, {'ProjectArn': second})
        assert checks.model_count(ctx, 'RUNNING')['usage'] == 2
        assert checks.model_count(ctx, 'TRAINING_IN_PROGRESS')['usage'] == 1
        assert checks.model_count(ctx, 'COPYING_IN_PROGRESS')['usage'] == 1
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('state', ['STARTING', 'STOPPING', 'DELETING', 'UNKNOWN', None])
def test_unresolved_model_running_reservations_are_not_zero(state):
    ctx = Mock()
    ctx.call.side_effect = [[{'ProjectArn': PROJECT}], [version(status=state)]]
    with pytest.raises(NoData):
        checks.model_count(ctx, 'RUNNING')


@pytest.mark.parametrize('changes', [{'ProjectVersionArn': PROJECT.replace('example', 'wrong')+'/version/v/1'},
                                    {'Feature': 'CONTENT_MODERATION'}, {'ProjectVersionArn': None}])
def test_model_identity_and_feature_mismatch_prevent_counts(changes):
    ctx = Mock()
    ctx.call.side_effect = [[{'ProjectArn': PROJECT}], [dict(version(), **changes)]]
    with pytest.raises(NoData):
        checks.model_count(ctx, 'RUNNING')


def test_inference_units_use_maximum_configured_capacity_per_running_model():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ProjectArn': PROJECT}],
        [version('fixed', MinInferenceUnits=2),
         version('scaling', MinInferenceUnits=1, MaxInferenceUnits=5),
         version('stopped', 'STOPPED')],
    ]
    result = checks.inference_units_per_running_model(ctx)
    assert result['usage'] == 5
    assert result['resource_id'].endswith('/version/scaling/1234567890')


@pytest.mark.parametrize('changes', [
    {},
    {'MinInferenceUnits': 0},
    {'MinInferenceUnits': 2, 'MaxInferenceUnits': 1},
    {'MinInferenceUnits': True},
])
def test_running_model_requires_valid_inference_unit_capacity(changes):
    ctx = Mock()
    ctx.call.side_effect = [[{'ProjectArn': PROJECT}], [version(**changes)]]
    with pytest.raises(NoData, match='invalid inference-unit capacity'):
        checks.inference_units_per_running_model(ctx)


@pytest.mark.parametrize('state', ['STARTING', 'STOPPING', 'DELETING'])
def test_transitional_model_inference_unit_reservations_are_unknown(state):
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ProjectArn': PROJECT}],
        [version(status=state, MinInferenceUnits=1, MaxInferenceUnits=2)],
    ]
    with pytest.raises(NoData, match='unresolved inference-unit reservation'):
        checks.inference_units_per_running_model(ctx)


def test_filtered_project_inventory_rejects_other_features():
    ctx = Mock()
    ctx.call.return_value = [{'ProjectArn': PROJECT, 'Feature': 'CONTENT_MODERATION'}]
    with pytest.raises(NoData):
        checks.CHECKS[0][2](ctx)
    ctx.call.assert_called_once_with('rekognition', 'describe_projects', 'ProjectDescriptions', Features=['CUSTOM_LABELS'])


def test_label_detection_starting_is_active_and_kinesis_associations_include_stopped_processors():
    ctx = context('L-0A2A7683')
    data = [processor(), processor('label', 'ConnectedHome', 'STARTING'), processor('idle', status='STOPPED', video=VIDEO+'2')]
    summaries = [{'Name': d['Name'], 'Status': d['Status']} for d in data]
    with Stubber(ctx.client('rekognition')) as stub:
        stub.add_response('list_stream_processors', {'StreamProcessors': summaries[:1], 'NextToken': 'next'}, {})
        stub.add_response('list_stream_processors', {'StreamProcessors': summaries,}, {'NextToken': 'next'})
        for item in data:
            stub.add_response('describe_stream_processor', item, {'Name': item['Name']})
        assert checks.stream_count(ctx, 'FaceSearch')['usage'] == 1
        assert checks.stream_count(ctx, 'ConnectedHome')['usage'] == 1
        inputs = checks.processors_per_stream(ctx)
        outputs = checks.processors_per_stream(ctx, output=True)
        assert (inputs['usage'], inputs['resource_id']) == (2, VIDEO)
        assert (outputs['usage'], outputs['resource_id']) == (2, OUTPUT)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('kind,state', [('FaceSearch', 'STARTING'), ('FaceSearch', 'STOPPING'),
                                      ('ConnectedHome', 'RUNNING'), ('ConnectedHome', 'UPDATING')])
def test_stream_transitions_are_unknown_for_the_affected_processor_type(kind, state):
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'processor', 'Status': state}], processor('processor', kind, state)]
    with pytest.raises(NoData):
        checks.stream_count(ctx, kind)


@pytest.mark.parametrize('changes', [{'Name': 'other'}, {'Status': 'STOPPED'}, {'Settings': {}},
                                    {'Settings': {'FaceSearch': {}, 'ConnectedHome': {'Labels': []}}}])
def test_inconsistent_processor_detail_is_not_counted(changes):
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'face', 'Status': 'RUNNING'}], dict(processor(), **changes)]
    with pytest.raises(NoData):
        checks.stream_count(ctx, 'FaceSearch')


def test_missing_kinesis_configuration_is_not_zero():
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'face', 'Status': 'RUNNING'}], dict(processor(), Output={})]
    with pytest.raises(NoData):
        checks.processors_per_stream(ctx, output=True)


def test_media_analysis_pagination_counts_running_jobs_only():
    ctx = context('L-22FA69BA')
    active = {'JobId': 'active', 'Status': 'IN_PROGRESS', 'CreationTimestamp': NOW, 'OperationsConfig': {},
              'Input': {'S3Object': {'Bucket': 'input-bucket', 'Name': 'manifest.json'}}, 'OutputConfig': {'S3Bucket': 'output-bucket'}}
    with Stubber(ctx.client('rekognition')) as stub:
        stub.add_response('list_media_analysis_jobs', {'MediaAnalysisJobs': [active], 'NextToken': 'next'}, {})
        stub.add_response('list_media_analysis_jobs', {'MediaAnalysisJobs': [active, dict(active, JobId='done', Status='SUCCEEDED')]}, {'NextToken': 'next'})
        result = checks.media_analysis_jobs(ctx)
        assert result['usage'] == 1
        assert 'manifest.json' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('state', ['CREATED', 'QUEUED', 'UNKNOWN'])
def test_unresolved_media_analysis_reservations_are_unknown(state):
    ctx = Mock()
    ctx.call.return_value = [{'JobId': 'job', 'Status': state}]
    with pytest.raises(NoData):
        checks.media_analysis_jobs(ctx)


def test_conflicting_duplicate_inventory_rejects_racing_status_updates():
    ctx = Mock()
    ctx.call.return_value = [{'JobId': 'job', 'Status': s} for s in ['IN_PROGRESS', 'SUCCEEDED']]
    with pytest.raises(NoData):
        checks.media_analysis_jobs(ctx)


def test_late_processor_error_prevents_partial_collector_result():
    ctx = context('L-8D9029A2')
    with Stubber(ctx.client('rekognition')) as stub:
        stub.add_response('list_stream_processors', {'StreamProcessors': [{'Name': 'face', 'Status': 'RUNNING'}, {'Name': 'later', 'Status': 'RUNNING'}]}, {})
        stub.add_response('describe_stream_processor', processor(), {'Name': 'face'})
        stub.add_client_error('describe_stream_processor', 'AccessDeniedException', expected_params={'Name': 'later'})
        row, = checks.get_current_quotastatus_rekognition(ctx=ctx, skip={('rekognition', code) for code, _, _ in checks.CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_checks_register_without_calls_for_absent_service_and_empty_inventories_are_zero():
    ctx = context()
    ctx.quotas = {}
    ctx.call = Mock(return_value=[])
    assert checks.get_current_quotastatus_rekognition(ctx=ctx) == []
    ctx.call.assert_not_called()
    for _, _, fn in checks.EXTENDED_CHECKS:
        assert fn(ctx)['usage'] == 0
    assert {('rekognition', code) for code, _, _ in checks.EXTENDED_CHECKS} <= custom_keys()
    for name in ['DescribeStreamProcessor', 'ListMediaAnalysisJobs']:
        assert grants(f'rekognition:{name}')
