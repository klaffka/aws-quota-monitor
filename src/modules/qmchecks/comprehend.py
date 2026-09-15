"""Amazon Comprehend job, model, flywheel, dataset and endpoint quotas.

Comprehend filters every listing server side, so the active job counts ask for
each unfinished status rather than listing a service's whole job history.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

COMPREHEND = 'comprehend'
JOB_STATES = {'SUBMITTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'STOP_REQUESTED',
              'STOPPED'}
RUNNING_JOB_STATES = ('SUBMITTED', 'IN_PROGRESS', 'STOP_REQUESTED')
MODEL_STATES = {'SUBMITTED', 'TRAINING', 'DELETING', 'STOP_REQUESTED', 'STOPPED',
                'IN_ERROR', 'TRAINED', 'TRAINED_WITH_WARNING'}
TRAINING_MODEL_STATES = ('SUBMITTED', 'TRAINING')
FLYWHEEL_STATES = {'CREATING', 'ACTIVE', 'UPDATING', 'DELETING', 'FAILED'}
DATASET_TYPES = {'TRAIN', 'TEST'}
ITERATION_STATES = {'TRAINING', 'EVALUATING', 'COMPLETED', 'FAILED', 'STOP_REQUESTED',
                    'STOPPED'}
RUNNING_ITERATION_STATES = {'TRAINING', 'EVALUATING', 'STOP_REQUESTED'}


def _active_jobs(method, key):
    """Count the jobs of one kind that Comprehend has not finished."""
    def check(ctx):
        usage = 0
        for status in RUNNING_JOB_STATES:
            for job in ctx.call(COMPREHEND, method, key,
                                Filter={'JobStatus': status}):
                reported = job.get('JobStatus')
                if reported is not None and reported not in JOB_STATES:
                    raise NoData('Comprehend job has an unknown status')
                usage += 1
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return dict(usage=usage, source=f'comprehend:{operation}',
                    method='ACCOUNT_COUNT')
    return check


def _training_models(method, key):
    def check(ctx):
        usage = 0
        for status in TRAINING_MODEL_STATES:
            for model in ctx.call(COMPREHEND, method, key,
                                  Filter={'Status': status}):
                reported = model.get('Status')
                if reported is not None and reported not in MODEL_STATES:
                    raise NoData('Comprehend model has an unknown status')
                usage += 1
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return dict(usage=usage, source=f'comprehend:{operation}',
                    method='ACCOUNT_COUNT')
    return check


def flywheels(ctx, status=None):
    found = {}
    arguments = {'Filter': {'Status': status}} if status else {}
    for flywheel in ctx.call(COMPREHEND, 'list_flywheels', 'FlywheelSummaryList',
                             **arguments):
        arn = flywheel.get('FlywheelArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Comprehend flywheel is missing its ARN')
        if flywheel.get('Status') not in FLYWHEEL_STATES:
            raise NoData('Comprehend flywheel has an unknown status')
        found[arn] = flywheel
    return found


def _flywheels_with_status(status):
    return lambda ctx: dict(usage=len(flywheels(ctx, status)),
                            source='comprehend:ListFlywheels',
                            method='ACCOUNT_COUNT')


def creating_datasets(ctx):
    usage = 0
    for flywheel in flywheels(ctx):
        usage += len(ctx.call(COMPREHEND, 'list_datasets', 'DatasetPropertiesList',
                              FlywheelArn=flywheel,
                              Filter={'Status': 'CREATING'}))
    return dict(usage=usage, source='comprehend:ListDatasets',
                method='ACCOUNT_COUNT')


def _datasets_of_type(dataset_type):
    def check(ctx):
        values = []
        for flywheel in flywheels(ctx):
            datasets = ctx.call(COMPREHEND, 'list_datasets', 'DatasetPropertiesList',
                                FlywheelArn=flywheel,
                                Filter={'DatasetType': dataset_type})
            for dataset in datasets:
                if dataset.get('DatasetType') not in DATASET_TYPES:
                    raise NoData('Comprehend dataset has an unknown type')
            values.append((flywheel, len(datasets), None))
        return maximum(values, 'ComprehendFlywheel', 'comprehend:ListDatasets')
    return check


def running_flywheel_iterations(ctx):
    usage = 0
    for flywheel in flywheels(ctx):
        for iteration in ctx.call(COMPREHEND, 'list_flywheel_iteration_history',
                                  'FlywheelIterationPropertiesList',
                                  FlywheelArn=flywheel):
            status = iteration.get('Status')
            if status not in ITERATION_STATES:
                raise NoData('Comprehend flywheel iteration has an unknown status')
            usage += status in RUNNING_ITERATION_STATES
    return dict(usage=usage, source='comprehend:ListFlywheelIterationHistory',
                method='ACCOUNT_COUNT')


def endpoints(ctx):
    found = {}
    for endpoint in ctx.call(COMPREHEND, 'list_endpoints', 'EndpointPropertiesList'):
        arn = endpoint.get('EndpointArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Comprehend endpoint is missing its ARN')
        units = endpoint.get('DesiredInferenceUnits')
        if units is not None and (not isinstance(units, int) or isinstance(units, bool)):
            raise NoData('Comprehend endpoint has invalid inference units')
        found[arn] = units or 0
    return found


def inference_units_per_account(ctx):
    return dict(usage=sum(endpoints(ctx).values()),
                source='comprehend:ListEndpoints', method='ACCOUNT_COUNT')


def inference_units_per_endpoint(ctx):
    return maximum(((arn, units, None) for arn, units in endpoints(ctx).items()),
                   'ComprehendEndpoint', 'comprehend:ListEndpoints')


JOB_QUOTAS = (
    ('L-E65FE76A', 'StartDocumentClassificationJob max active jobs',
     'list_document_classification_jobs', 'DocumentClassificationJobPropertiesList'),
    ('L-7AC96081', 'StartDominantLanguageDetectionJob max active jobs',
     'list_dominant_language_detection_jobs',
     'DominantLanguageDetectionJobPropertiesList'),
    ('L-2B8ECCAB', 'StartEntitiesDetectionJob max active jobs',
     'list_entities_detection_jobs', 'EntitiesDetectionJobPropertiesList'),
    ('L-471B41D6', 'StartEventsDetectionJob max active jobs',
     'list_events_detection_jobs', 'EventsDetectionJobPropertiesList'),
    ('L-BFFD1421', 'StartKeyPhrasesDetectionJob max active jobs',
     'list_key_phrases_detection_jobs', 'KeyPhrasesDetectionJobPropertiesList'),
    ('L-D88E2B98', 'StartPiiEntitiesDetectionJob max active jobs',
     'list_pii_entities_detection_jobs', 'PiiEntitiesDetectionJobPropertiesList'),
    ('L-32ABBB12', 'StartSentimentDetectionJob max active jobs',
     'list_sentiment_detection_jobs', 'SentimentDetectionJobPropertiesList'),
    ('L-358FBC4F', 'StartTargetedSentimentDetectionJob max active jobs',
     'list_targeted_sentiment_detection_jobs',
     'TargetedSentimentDetectionJobPropertiesList'),
    ('L-F2BED405', 'StartTopicsDetectionJob max active jobs',
     'list_topics_detection_jobs', 'TopicsDetectionJobPropertiesList'),
)

CHECKS = [
    ('L-55642075', 'Endpoints max active endpoints',
     lambda ctx: dict(usage=len(endpoints(ctx)), source='comprehend:ListEndpoints',
                      method='ACCOUNT_COUNT')),
    *[(code, name, _active_jobs(method, key))
      for code, name, method, key in JOB_QUOTAS],
    ('L-94042C4D', 'CreateDocumentClassifier max active jobs',
     _training_models('list_document_classifiers',
                      'DocumentClassifierPropertiesList')),
    ('L-4BDB4A9D', 'CreateEntityRecognizer max active jobs',
     _training_models('list_entity_recognizers', 'EntityRecognizerPropertiesList')),
    ('L-AE5B911F', 'CreateFlywheel max active flywheels',
     _flywheels_with_status('ACTIVE')),
    ('L-8F55B05C', 'CreateFlywheel max concurrent',
     _flywheels_with_status('CREATING')),
    ('L-0C094DCD', 'Datasets max concurrent creates', creating_datasets),
    ('L-7CC66BB8', 'MaxTrainDatasets per flywheel', _datasets_of_type('TRAIN')),
    ('L-1666A7DF', 'MaxTestDatasets per flywheel', _datasets_of_type('TEST')),
    ('L-C5F124CF', 'StartFlywheelIteration max concurrent flywheel iterations',
     running_flywheel_iterations),
    ('L-2A73DEBC', 'Endpoints max inference units per account',
     inference_units_per_account),
    ('L-70EC2949', 'Endpoints max inference units per endpoint',
     inference_units_per_endpoint),
]


def get_current_quotastatus_comprehend(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'comprehend' for service, _ in context.quotas):
        return []
    return context.run('comprehend', CHECKS, skip)
