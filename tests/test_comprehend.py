import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import comprehend
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

FLYWHEEL = 'arn:aws:comprehend:eu-central-1:123456789012:flywheel/reviews'
OTHER_FLYWHEEL = 'arn:aws:comprehend:eu-central-1:123456789012:flywheel/tickets'
ENDPOINT = 'arn:aws:comprehend:eu-central-1:123456789012:document-classifier-endpoint/a'


def context(code='L-55642075'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'comprehend', 'QuotaCode': code, 'Value': 10}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in comprehend.CHECKS if quota == code)


def test_active_jobs_ask_for_each_unfinished_status():
    ctx = context('L-32ABBB12')
    with Stubber(ctx.client('comprehend')) as stub:
        stub.add_response('list_sentiment_detection_jobs',
                          {'SentimentDetectionJobPropertiesList': [
                              {'JobId': 'a', 'JobStatus': 'SUBMITTED'}]},
                          {'Filter': {'JobStatus': 'SUBMITTED'}})
        stub.add_response('list_sentiment_detection_jobs',
                          {'SentimentDetectionJobPropertiesList': [
                              {'JobId': 'b', 'JobStatus': 'IN_PROGRESS'},
                              {'JobId': 'c', 'JobStatus': 'IN_PROGRESS'}]},
                          {'Filter': {'JobStatus': 'IN_PROGRESS'}})
        stub.add_response('list_sentiment_detection_jobs',
                          {'SentimentDetectionJobPropertiesList': []},
                          {'Filter': {'JobStatus': 'STOP_REQUESTED'}})
        assert check('L-32ABBB12')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_training_models_count_submitted_and_training_only():
    ctx = context('L-94042C4D')
    with Stubber(ctx.client('comprehend')) as stub:
        stub.add_response('list_document_classifiers',
                          {'DocumentClassifierPropertiesList': [
                              {'DocumentClassifierArn': 'a', 'Status': 'SUBMITTED'}]},
                          {'Filter': {'Status': 'SUBMITTED'}})
        stub.add_response('list_document_classifiers',
                          {'DocumentClassifierPropertiesList': [
                              {'DocumentClassifierArn': 'b', 'Status': 'TRAINING'}]},
                          {'Filter': {'Status': 'TRAINING'}})
        assert check('L-94042C4D')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def flywheel(arn, status='ACTIVE'):
    return {'FlywheelArn': arn, 'Status': status, 'ModelType': 'DOCUMENT_CLASSIFIER'}


def test_flywheels_are_counted_by_status():
    for code, status, expected in (('L-AE5B911F', 'ACTIVE', 2),
                                   ('L-8F55B05C', 'CREATING', 1)):
        ctx = context(code)
        with Stubber(ctx.client('comprehend')) as stub:
            entries = ([flywheel(FLYWHEEL), flywheel(OTHER_FLYWHEEL)]
                       if status == 'ACTIVE' else [flywheel(FLYWHEEL, 'CREATING')])
            stub.add_response('list_flywheels', {'FlywheelSummaryList': entries},
                              {'Filter': {'Status': status}})
            assert check(code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_an_unknown_flywheel_status_raises_nodata():
    ctx = context('L-AE5B911F')
    with Stubber(ctx.client('comprehend')) as stub:
        stub.add_response('list_flywheels', {'FlywheelSummaryList': [
            {'FlywheelArn': FLYWHEEL, 'Status': 'SPINNING'}]},
            {'Filter': {'Status': 'ACTIVE'}})
        with pytest.raises(NoData, match='unknown status'):
            check('L-AE5B911F')(ctx)


def test_datasets_are_counted_per_flywheel_and_type():
    ctx = context('L-7CC66BB8')
    with Stubber(ctx.client('comprehend')) as stub:
        stub.add_response('list_flywheels', {'FlywheelSummaryList': [
            flywheel(FLYWHEEL), flywheel(OTHER_FLYWHEEL)]}, {})
        stub.add_response('list_datasets', {'DatasetPropertiesList': [
            {'DatasetArn': 'a', 'DatasetType': 'TRAIN'}]},
            {'FlywheelArn': FLYWHEEL, 'Filter': {'DatasetType': 'TRAIN'}})
        stub.add_response('list_datasets', {'DatasetPropertiesList': [
            {'DatasetArn': 'b', 'DatasetType': 'TRAIN'},
            {'DatasetArn': 'c', 'DatasetType': 'TRAIN'}]},
            {'FlywheelArn': OTHER_FLYWHEEL, 'Filter': {'DatasetType': 'TRAIN'}})
        result = check('L-7CC66BB8')(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_FLYWHEEL)
        stub.assert_no_pending_responses()


def test_running_flywheel_iterations_exclude_finished_ones():
    ctx = context('L-C5F124CF')
    with Stubber(ctx.client('comprehend')) as stub:
        stub.add_response('list_flywheels', {'FlywheelSummaryList': [
            flywheel(FLYWHEEL)]}, {})
        stub.add_response('list_flywheel_iteration_history', {
            'FlywheelIterationPropertiesList': [
                {'FlywheelArn': FLYWHEEL, 'Status': 'TRAINING'},
                {'FlywheelArn': FLYWHEEL, 'Status': 'EVALUATING'},
                {'FlywheelArn': FLYWHEEL, 'Status': 'COMPLETED'}]},
            {'FlywheelArn': FLYWHEEL})
        assert comprehend.running_flywheel_iterations(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_inference_units_are_summed_and_maximised():
    entries = [{'EndpointArn': ENDPOINT, 'DesiredInferenceUnits': 3},
               {'EndpointArn': f'{ENDPOINT}-2', 'DesiredInferenceUnits': 5}]
    for code, expected_usage, expected_id in (('L-2A73DEBC', 8, None),
                                              ('L-70EC2949', 5, f'{ENDPOINT}-2')):
        ctx = context(code)
        with Stubber(ctx.client('comprehend')) as stub:
            stub.add_response('list_endpoints', {'EndpointPropertiesList': entries}, {})
            result = check(code)(ctx)
            assert result['usage'] == expected_usage, code
            assert result.get('resource_id') == expected_id, code
            stub.assert_no_pending_responses()


def test_every_comprehend_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'comprehend'}
    assert {code for code, _, _ in comprehend.CHECKS} <= registered
