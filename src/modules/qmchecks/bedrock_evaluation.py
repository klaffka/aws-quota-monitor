"""Bedrock model evaluation and model import job quotas."""
from functools import partial

from modules.qmcore.aws import NoData, maximum


def unique_jobs(items):
    result = {}
    for item in items:
        arn = item.get('jobArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Bedrock job inventory has no job ARN')
        if arn in result and result[arn] != item:
            raise NoData('Bedrock job changed during pagination')
        result[arn] = item
    return list(result.values())


def evaluation_jobs(ctx):
    # Model quotas must not include knowledge-base/RAG evaluations. Filtering
    # explicitly also scopes legacy summaries with no applicationType field.
    jobs = unique_jobs(ctx.call('bedrock', 'list_evaluation_jobs', 'jobSummaries',
                                applicationTypeEquals='ModelEvaluation'))
    if any(job.get('applicationType', 'ModelEvaluation') != 'ModelEvaluation' for job in jobs):
        raise NoData('Bedrock model evaluation inventory returned another application type')
    return jobs


def evaluation_count(ctx, job_type=None):
    jobs = evaluation_jobs(ctx)
    if job_type is None:
        count = len(jobs)
    else:
        count = 0
        for job in jobs:
            if job.get('jobType') not in {'Human', 'Automated'}:
                raise NoData('Bedrock evaluation has an unknown job type')
            if job['jobType'] != job_type:
                continue
            status = job.get('status')
            if status == 'InProgress':
                count += 1
            elif status not in {'Completed', 'Failed', 'Stopped'}:
                raise NoData('Bedrock evaluation has an unresolved concurrent-job reservation')
    return dict(usage=count, source='bedrock:ListEvaluationJobs', method='ACCOUNT_COUNT')


def evaluation_definitions(ctx, job_type):
    for job in evaluation_jobs(ctx):
        if job.get('jobType') not in {'Human', 'Automated'}:
            raise NoData('Bedrock evaluation has an unknown job type')
        if job['jobType'] != job_type:
            continue
        arn = job['jobArn']
        data = ctx.call('bedrock', 'get_evaluation_job', jobIdentifier=arn)
        if (data.get('jobArn') != arn or data.get('jobType') != job_type
                or data.get('applicationType', 'ModelEvaluation') != 'ModelEvaluation'):
            raise NoData('Bedrock evaluation detail has an inconsistent identity or type')
        config = data.get('evaluationConfig')
        if not isinstance(config, dict) or set(config) != {job_type.lower()}:
            raise NoData('Bedrock evaluation has no unambiguous configuration')
        settings = config[job_type.lower()]
        if not isinstance(settings, dict):
            raise NoData('Bedrock evaluation settings are missing')
        yield arn, data, settings


def required_list(config, field, optional=False):
    value = config.get(field, [] if optional else None)
    if not isinstance(value, list) or (not optional and not value):
        raise NoData('Bedrock evaluation configuration is missing a measured list')
    return value


def evaluation_configuration(ctx, job_type, measure):
    values = []
    for arn, data, config in evaluation_definitions(ctx, job_type):
        if measure == 'models':
            inference = data.get('inferenceConfig')
            if not isinstance(inference, dict) or set(inference) != {'models'}:
                raise NoData('Model evaluation has no unambiguous model configuration')
            count = len(required_list(inference, 'models'))
        elif measure == 'customMetrics':
            count = len(required_list(config, 'customMetrics', optional=True))
        else:
            datasets = required_list(config, 'datasetMetricConfigs')
            if any(not isinstance(item, dict) for item in datasets):
                raise NoData('Model evaluation has an invalid dataset configuration')
            if measure == 'metrics':
                for index, item in enumerate(datasets):
                    values.append((f'{arn}/dataset/{index}', len(required_list(item, 'metricNames')), None))
                continue
            if measure == 'customDatasets':
                count = 0
                for item in datasets:
                    dataset = item.get('dataset')
                    if not isinstance(dataset, dict):
                        raise NoData('Model evaluation has no dataset definition')
                    if not isinstance(dataset.get('name'), str) or not dataset['name']:
                        raise NoData('Model evaluation dataset has no name')
                    if 'datasetLocation' in dataset:
                        location = dataset['datasetLocation']
                        if not isinstance(location, dict) or not location.get('s3Uri'):
                            raise NoData('Model evaluation custom dataset has no S3 location')
                        count += 1
            else:
                count = len(datasets)
        values.append((arn, count, None))
    return maximum(values, 'ModelEvaluationDataset' if measure == 'metrics' else 'ModelEvaluationJob',
                   'bedrock:GetEvaluationJob')


def import_jobs(ctx):
    count = 0
    for job in unique_jobs(ctx.call('bedrock', 'list_model_import_jobs', 'modelImportJobSummaries')):
        if job.get('status') == 'InProgress':
            count += 1
        elif job.get('status') not in {'Completed', 'Failed'}:
            raise NoData('Bedrock import job has an unknown status')
    return dict(usage=count, source='bedrock:ListModelImportJobs', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-5F098EFA', 'Concurrent model import jobs', import_jobs),
    ('L-24CCD302', 'Number of evaluation jobs', evaluation_count),
    ('L-557C8C47', 'Concurrent automatic model evaluation jobs', partial(evaluation_count, job_type='Automated')),
    ('L-973C31D1', 'Concurrent human model evaluation jobs', partial(evaluation_count, job_type='Human')),
    ('L-61D10141', 'Models per human evaluation job', partial(evaluation_configuration, job_type='Human', measure='models')),
    ('L-8AB6E28F', 'Models per automatic evaluation job', partial(evaluation_configuration, job_type='Automated', measure='models')),
    ('L-FD0CC292', 'Datasets per automatic evaluation job', partial(evaluation_configuration, job_type='Automated', measure='datasets')),
    ('L-FAF1E3E4', 'Metrics per automatic evaluation dataset', partial(evaluation_configuration, job_type='Automated', measure='metrics')),
    ('L-FDA23835', 'Custom metrics per human evaluation job', partial(evaluation_configuration, job_type='Human', measure='customMetrics')),
    ('L-E939CCA4', 'Custom prompt datasets per human evaluation job', partial(evaluation_configuration, job_type='Human', measure='customDatasets')),
]
