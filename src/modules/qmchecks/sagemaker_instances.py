"""SageMaker instance-type usage for the families AWS publishes no metric for.

Almost every ``<type> for <kind> job usage`` quota carries a CloudWatch usage
metric, which counts as covered without a check. The ml.p3 training, spot
training, warm pool and processing quotas do not, so they are counted from the
jobs themselves. The mechanism is not tied to ml.p3; only the codes are.
"""
from modules.qmcore.aws import NoData

SAGEMAKER = 'sagemaker'
# A terminated warm pool has released its instances; the other three still hold
# them, and the listing filters by exactly one state at a time.
WARM_POOL_HOLDING = ('Available', 'InUse', 'Reused')
SOURCE_TRAINING = 'sagemaker:ListTrainingJobs+DescribeTrainingJob'
SOURCE_PROCESSING = 'sagemaker:ListProcessingJobs+DescribeProcessingJob'


def _count(entry, instance_type):
    """Instances of one type in a resource or cluster configuration entry.

    Flexible training resolves the type it actually got into ``Selected*``, so
    that answer wins over the type the job asked for.
    """
    chosen = entry.get('SelectedInstanceType') or entry.get('InstanceType')
    if chosen != instance_type:
        return 0
    count = entry.get('SelectedInstanceCount')
    if count is None:
        count = entry.get('InstanceCount')
    if not isinstance(count, int):
        raise NoData('SageMaker job configuration has no instance count')
    return count


def _configured(config, instance_type):
    """A job states either one instance type or a set of instance groups."""
    groups = config.get('InstanceGroups')
    if groups:
        return sum(_count(group, instance_type) for group in groups)
    return _count(config, instance_type)


def _training_jobs(ctx, **arguments):
    for job in ctx.call(SAGEMAKER, 'list_training_jobs', 'TrainingJobSummaries', **arguments):
        name = job.get('TrainingJobName')
        if not isinstance(name, str) or not name:
            raise NoData('SageMaker training job is missing its name')
        detail = ctx.call(SAGEMAKER, 'describe_training_job', TrainingJobName=name)
        if detail.get('TrainingJobName') != name:
            raise NoData('SageMaker training job detail has a different identity')
        yield detail


def training_instances(ctx, instance_type, *, spot):
    """Managed spot capacity is bounded apart from on-demand capacity."""
    usage = 0
    for detail in _training_jobs(ctx, StatusEquals='InProgress'):
        if bool(detail.get('EnableManagedSpotTraining')) is not spot:
            continue
        usage += _configured(detail.get('ResourceConfig') or {}, instance_type)
    return dict(usage=usage, source=SOURCE_TRAINING, method='ACCOUNT_SUM',
                meta={'instanceType': instance_type})


def warm_pool_instances(ctx, instance_type):
    usage = 0
    for status in WARM_POOL_HOLDING:
        for detail in _training_jobs(ctx, WarmPoolStatusEquals=status):
            usage += _configured(detail.get('ResourceConfig') or {}, instance_type)
    return dict(usage=usage, source=SOURCE_TRAINING, method='ACCOUNT_SUM',
                meta={'instanceType': instance_type})


def processing_instances(ctx, instance_type):
    usage = 0
    for job in ctx.call(SAGEMAKER, 'list_processing_jobs', 'ProcessingJobSummaries',
                        StatusEquals='InProgress'):
        name = job.get('ProcessingJobName')
        if not isinstance(name, str) or not name:
            raise NoData('SageMaker processing job is missing its name')
        detail = ctx.call(SAGEMAKER, 'describe_processing_job', ProcessingJobName=name)
        if detail.get('ProcessingJobName') != name:
            raise NoData('SageMaker processing job detail has a different identity')
        cluster = (detail.get('ProcessingResources') or {}).get('ClusterConfig') or {}
        usage += _configured(cluster, instance_type)
    return dict(usage=usage, source=SOURCE_PROCESSING, method='ACCOUNT_SUM',
                meta={'instanceType': instance_type})


# One row per instance type: training, spot training, warm pool, processing.
UNMETERED_TYPES = (
    ('ml.p3.2xlarge', 'L-D438008E', 'L-2D4C6493', 'L-E3709F6E', 'L-0323EDB4'),
    ('ml.p3.8xlarge', 'L-558F1246', 'L-0201B959', 'L-5CA5BEE6', 'L-23EDF20C'),
    ('ml.p3.16xlarge', 'L-A99E0304', 'L-D58A90BB', 'L-763CF8E3', 'L-C5621FC4'),
)


def _build():
    checks = []
    for kind, training, spot, warm, processing in UNMETERED_TYPES:
        checks += [
            (training, f'{kind} for training job usage',
             lambda ctx, kind=kind: training_instances(ctx, kind, spot=False)),
            (spot, f'{kind} for spot training job usage',
             lambda ctx, kind=kind: training_instances(ctx, kind, spot=True)),
            (warm, f'{kind} for training warm pool usage',
             lambda ctx, kind=kind: warm_pool_instances(ctx, kind)),
            (processing, f'{kind} for processing job usage',
             lambda ctx, kind=kind: processing_instances(ctx, kind)),
        ]
    return checks


CHECKS = _build()
