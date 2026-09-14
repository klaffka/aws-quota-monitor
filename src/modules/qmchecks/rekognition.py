"""Amazon Rekognition Custom Labels project inventory."""
from collections import Counter
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, session_from_env, maximum


def projects(ctx):
    items = ctx.call('rekognition', 'describe_projects', 'ProjectDescriptions', Features=['CUSTOM_LABELS'])
    if any(item.get('Feature', 'CUSTOM_LABELS') != 'CUSTOM_LABELS' for item in items):
        raise NoData('Custom Labels project inventory returned another feature')
    return items


def required_id(item, field):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Rekognition inventory is missing {field}')
    return value


def unique(items, field):
    result = {}
    for item in items:
        identity = required_id(item, field)
        if identity in result and result[identity] != item:
            raise NoData('Rekognition inventory changed during pagination')
        result[identity] = item
    return result.values()

def models_per_project(ctx):
    values = []
    for project in projects(ctx):
        arn = project.get('ProjectArn')
        if arn:
            versions = ctx.call('rekognition', 'describe_project_versions',
                                'ProjectVersionDescriptions', ProjectArn=arn)
            values.append((arn, len(versions), None))
    return maximum(values, 'RekognitionProject', 'rekognition:DescribeProjectVersions')


def project_policies_per_project(ctx):
    values = []
    for project in projects(ctx):
        arn = project.get('ProjectArn')
        if arn:
            policies = ctx.call('rekognition', 'list_project_policies', 'ProjectPolicies', ProjectArn=arn)
            values.append((arn, len(policies), None))
    return maximum(values, 'RekognitionProject', 'rekognition:DescribeProjects+ListProjectPolicies')


MODEL_STATES = {
    'TRAINING_IN_PROGRESS', 'TRAINING_COMPLETED', 'TRAINING_FAILED', 'STARTING', 'RUNNING',
    'FAILED', 'STOPPING', 'STOPPED', 'DELETING', 'COPYING_IN_PROGRESS', 'COPYING_COMPLETED',
    'COPYING_FAILED', 'DEPRECATED', 'EXPIRED',
}


def model_count(ctx, target):
    count = 0
    for project in unique(projects(ctx), 'ProjectArn'):
        arn = project['ProjectArn']
        version_prefix = arn.rsplit('/', 1)[0] + '/version/'
        versions = ctx.call('rekognition', 'describe_project_versions', 'ProjectVersionDescriptions', ProjectArn=arn)
        for version in unique(versions, 'ProjectVersionArn'):
            if (not version['ProjectVersionArn'].startswith(version_prefix)
                    or version.get('Feature', 'CUSTOM_LABELS') != 'CUSTOM_LABELS'):
                raise NoData('Rekognition model version has a different parent or feature')
            state = version.get('Status')
            if state not in MODEL_STATES:
                raise NoData('Rekognition model version has an unknown status')
            if state == 'DELETING' or (target == 'RUNNING' and state in {'STARTING', 'STOPPING'}):
                raise NoData('Rekognition model has an unresolved concurrent quota reservation')
            count += state == target
    return dict(usage=count, source='rekognition:DescribeProjects+DescribeProjectVersions', method='ACCOUNT_COUNT')


def inference_units_per_running_model(ctx):
    values = []
    for project in unique(projects(ctx), 'ProjectArn'):
        arn = project['ProjectArn']
        version_prefix = arn.rsplit('/', 1)[0] + '/version/'
        versions = ctx.call('rekognition', 'describe_project_versions',
                            'ProjectVersionDescriptions', ProjectArn=arn)
        for version in unique(versions, 'ProjectVersionArn'):
            version_arn = version['ProjectVersionArn']
            if (not version_arn.startswith(version_prefix)
                    or version.get('Feature', 'CUSTOM_LABELS') != 'CUSTOM_LABELS'):
                raise NoData('Rekognition model version has a different parent or feature')
            state = version.get('Status')
            if state not in MODEL_STATES:
                raise NoData('Rekognition model version has an unknown status')
            if state in {'STARTING', 'STOPPING', 'DELETING'}:
                raise NoData('Rekognition model has an unresolved inference-unit reservation')
            if state != 'RUNNING':
                continue
            minimum = version.get('MinInferenceUnits')
            maximum_units = version.get('MaxInferenceUnits', minimum)
            if (not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1
                    or not isinstance(maximum_units, int) or isinstance(maximum_units, bool)
                    or maximum_units < minimum):
                raise NoData('Running Rekognition model has invalid inference-unit capacity')
            values.append((version_arn, maximum_units, None))
    return maximum(values, 'RekognitionProjectVersion',
                   'rekognition:DescribeProjects+DescribeProjectVersions')


def stream_definitions(ctx):
    summaries = ctx.call('rekognition', 'list_stream_processors', 'StreamProcessors')
    for item in unique(summaries, 'Name'):
        name = item['Name']
        data = ctx.call('rekognition', 'describe_stream_processor', Name=name)
        if data.get('Name') != name:
            raise NoData('Rekognition stream processor detail has another identity')
        if item.get('Status') != data.get('Status'):
            raise NoData('Rekognition stream processor status changed during collection')
        settings = data.get('Settings')
        if not isinstance(settings, dict) or set(settings) not in ({'FaceSearch'}, {'ConnectedHome'}):
            raise NoData('Rekognition stream processor has an unresolved type')
        kind = next(iter(settings))
        yield name, kind, data


def stream_count(ctx, kind):
    count = 0
    for _, processor_kind, data in stream_definitions(ctx):
        if processor_kind != kind:
            continue
        state = data.get('Status')
        # Label detection remains STARTING for the entire processing run;
        # FaceSearch enters RUNNING. These are intentionally different.
        active = 'STARTING' if kind == 'ConnectedHome' else 'RUNNING'
        if state == active:
            count += 1
        elif state not in {'STOPPED', 'FAILED'}:
            raise NoData('Rekognition stream processor has an unresolved concurrency state')
    return dict(usage=count, source='rekognition:ListStreamProcessors+DescribeStreamProcessor', method='ACCOUNT_COUNT')


def processors_per_stream(ctx, output=False):
    counts = Counter()
    for _, kind, data in stream_definitions(ctx):
        if output and kind != 'FaceSearch':
            continue
        wrapper, field = ('Output', 'KinesisDataStream') if output else ('Input', 'KinesisVideoStream')
        config = data.get(wrapper)
        if not isinstance(config, dict) or not isinstance(config.get(field), dict):
            raise NoData('Rekognition processor has no configured Kinesis stream')
        arn = required_id(config[field], 'Arn')
        counts[arn] += 1
    return maximum([(arn, count, None) for arn, count in counts.items()],
                   'KinesisDataStream' if output else 'KinesisVideoStream', 'rekognition:DescribeStreamProcessor')


def media_analysis_jobs(ctx):
    count = 0
    for job in unique(ctx.call('rekognition', 'list_media_analysis_jobs', 'MediaAnalysisJobs'), 'JobId'):
        state = job.get('Status')
        if state == 'IN_PROGRESS':
            count += 1
        elif state not in {'SUCCEEDED', 'FAILED'}:
            raise NoData('Rekognition media analysis job has an unresolved concurrent reservation')
    return dict(usage=count, source='rekognition:ListMediaAnalysisJobs', method='ACCOUNT_COUNT')


CHECKS = [('L-14D0BC19', 'Custom Labels projects per account',
           lambda ctx: dict(usage=len(projects(ctx)),
                            source='rekognition:DescribeProjects', method='ACCOUNT_COUNT')),
          ('L-9CF05323', 'Custom Labels models per project', models_per_project),
          ('L-0B2CE4DD', 'Project policies per project', project_policies_per_project),
          ('L-01C8D885', 'Stream processors per account',
           lambda ctx: dict(usage=len(ctx.call('rekognition', 'list_stream_processors', 'StreamProcessors')),
                            source='rekognition:ListStreamProcessors', method='ACCOUNT_COUNT'))]

EXTENDED_CHECKS = [
    ('L-4FA65ECB', 'Maximum inference units per running Custom Labels model',
     inference_units_per_running_model),
    ('L-5E225387', 'Concurrently running Custom Labels models', partial(model_count, target='RUNNING')),
    ('L-F1558568', 'Concurrent Custom Labels training jobs', partial(model_count, target='TRAINING_IN_PROGRESS')),
    ('L-B3EE7891', 'Concurrent Custom Labels model copy jobs', partial(model_count, target='COPYING_IN_PROGRESS')),
    ('L-8D9029A2', 'Concurrent face search stream processors', partial(stream_count, kind='FaceSearch')),
    ('L-0A2A7683', 'Concurrent label detection stream processors', partial(stream_count, kind='ConnectedHome')),
    ('L-3269D948', 'Stream processors per Kinesis video input stream', processors_per_stream),
    ('L-70336415', 'Face search processors per Kinesis data output stream', partial(processors_per_stream, output=True)),
    ('L-22FA69BA', 'Concurrent Media Analysis jobs', media_analysis_jobs),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_rekognition(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rekognition' for service, _ in context.quotas): return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS if ('rekognition', check[0]) in context.quotas]
    return context.run('rekognition', checks, skip)
