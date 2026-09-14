"""Amazon Personalize regional resource and in-flight job quotas."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


SERVICE = 'personalize'
RESOURCE_STATES = {
    'CREATE PENDING', 'CREATE IN_PROGRESS', 'ACTIVE', 'CREATE FAILED',
    'DELETE PENDING', 'DELETE IN_PROGRESS',
}
DATASET_GROUP_STATES = RESOURCE_STATES - {'DELETE IN_PROGRESS'}
RECOMMENDER_STATES = RESOURCE_STATES | {
    'INACTIVE', 'STOP PENDING', 'STOP IN_PROGRESS',
    'START PENDING', 'START IN_PROGRESS',
}
BATCH_JOB_STATES = {'PENDING', 'IN PROGRESS', 'ACTIVE', 'CREATE FAILED'}
SOLUTION_VERSION_STATES = {
    'CREATE PENDING', 'CREATE IN_PROGRESS', 'ACTIVE', 'CREATE FAILED',
    'CREATE STOPPING', 'CREATE STOPPED',
}
DATA_DELETION_STATES = {'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED'}


def _validate_arn(arn, ctx, prefix, subject):
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != SERVICE
            or parts[3] != ctx.region or parts[4] != ctx.account
            or not parts[5].startswith(prefix)
            or len(parts[5]) <= len(prefix)):
        raise NoData(f'Personalize {subject} has an inconsistent ARN')


def _inventory(ctx, method, key, identity, prefix, subject, *, states=None,
               counted=None, **kwargs):
    result = {}
    for item in ctx.call(SERVICE, method, key, **kwargs):
        if not isinstance(item, dict):
            raise NoData(f'Personalize {subject} inventory contains an invalid item')
        arn = item.get(identity)
        _validate_arn(arn, ctx, prefix, subject)
        if states is not None and item.get('status') not in states:
            raise NoData(f'Personalize {subject} has an unknown state')
        if arn in result:
            if result[arn] != item:
                raise NoData(f'Personalize {subject} changed during pagination')
            continue
        result[arn] = item
    if counted is not None:
        result = {arn: item for arn, item in result.items()
                  if item['status'] in counted}
    return result


def dataset_groups(ctx, *, active_only=False):
    return _inventory(
        ctx, 'list_dataset_groups', 'datasetGroups', 'datasetGroupArn',
        'dataset-group/', 'dataset group', states=DATASET_GROUP_STATES,
        counted={'ACTIVE'} if active_only else None)


def active_dataset_group_count(ctx):
    return dict(usage=len(dataset_groups(ctx, active_only=True)),
                source='personalize:ListDatasetGroups', method='ACCOUNT_COUNT')


def active_solutions_by_group(ctx):
    result = {}
    for group_arn in dataset_groups(ctx, active_only=True):
        items = _inventory(
            ctx, 'list_solutions', 'solutions', 'solutionArn', 'solution/',
            'solution', states=RESOURCE_STATES, counted={'ACTIVE'},
            datasetGroupArn=group_arn)
        for solution_arn in items:
            if solution_arn in result:
                raise NoData('Personalize solution appears in multiple dataset groups')
            result[solution_arn] = group_arn
    return result


def active_solutions_per_group(ctx):
    groups = dataset_groups(ctx, active_only=True)
    counts = Counter(active_solutions_by_group(ctx).values())
    return maximum(((arn, counts[arn], None) for arn in groups),
                   'PersonalizeDatasetGroup',
                   'personalize:ListDatasetGroups+ListSolutions')


def active_campaigns_per_group(ctx):
    groups = dataset_groups(ctx, active_only=True)
    counts = Counter()
    seen = {}
    for solution_arn, group_arn in active_solutions_by_group(ctx).items():
        items = _inventory(
            ctx, 'list_campaigns', 'campaigns', 'campaignArn', 'campaign/',
            'campaign', states=RESOURCE_STATES, counted={'ACTIVE'},
            solutionArn=solution_arn)
        for campaign_arn, item in items.items():
            if campaign_arn in seen and seen[campaign_arn] != item:
                raise NoData('Personalize campaign changed between parent inventories')
            if campaign_arn in seen:
                raise NoData('Personalize campaign appears under multiple solutions')
            seen[campaign_arn] = item
            counts[group_arn] += 1
    return maximum(((arn, counts[arn], None) for arn in groups),
                   'PersonalizeDatasetGroup',
                   'personalize:ListDatasetGroups+ListSolutions+ListCampaigns')


def recommenders_per_group(ctx):
    groups = dataset_groups(ctx, active_only=True)
    values = []
    seen = set()
    for group_arn in groups:
        items = _inventory(
            ctx, 'list_recommenders', 'recommenders', 'recommenderArn',
            'recommender/', 'recommender', states=RECOMMENDER_STATES,
            datasetGroupArn=group_arn)
        for arn, item in items.items():
            if item.get('datasetGroupArn') != group_arn:
                raise NoData('Personalize recommender has an inconsistent parent')
            if arn in seen:
                raise NoData('Personalize recommender appears in multiple dataset groups')
            seen.add(arn)
        values.append((group_arn, len(items), None))
    return maximum(values, 'PersonalizeDatasetGroup',
                   'personalize:ListDatasetGroups+ListRecommenders')


def active_filter_count_per_group(ctx):
    groups = dataset_groups(ctx, active_only=True)
    values = []
    seen = set()
    for group_arn in groups:
        items = _inventory(
            ctx, 'list_filters', 'Filters', 'filterArn', 'filter/', 'filter',
            states=RESOURCE_STATES, datasetGroupArn=group_arn)
        for arn, item in items.items():
            if item.get('datasetGroupArn') != group_arn:
                raise NoData('Personalize filter has an inconsistent parent')
            if arn in seen:
                raise NoData('Personalize filter appears in multiple dataset groups')
            seen.add(arn)
        values.append((group_arn,
                       sum(item['status'] == 'ACTIVE' for item in items.values()),
                       None))
    return maximum(values, 'PersonalizeDatasetGroup',
                   'personalize:ListDatasetGroups+ListFilters')


def schema_count(ctx):
    items = _inventory(ctx, 'list_schemas', 'schemas', 'schemaArn', 'schema/',
                       'schema')
    return dict(usage=len(items), source='personalize:ListSchemas',
                method='ACCOUNT_COUNT')


def pending_batch_inference_jobs(ctx):
    items = _inventory(
        ctx, 'list_batch_inference_jobs', 'batchInferenceJobs',
        'batchInferenceJobArn', 'batch-inference-job/', 'batch inference job',
        states=BATCH_JOB_STATES, counted={'PENDING', 'IN PROGRESS'})
    return dict(usage=len(items), source='personalize:ListBatchInferenceJobs',
                method='ACCOUNT_COUNT')


def pending_solution_versions(ctx):
    items = _inventory(
        ctx, 'list_solution_versions', 'solutionVersions', 'solutionVersionArn',
        'solution/', 'solution version', states=SOLUTION_VERSION_STATES,
        counted={'CREATE PENDING', 'CREATE IN_PROGRESS'})
    return dict(usage=len(items), source='personalize:ListSolutionVersions',
                method='ACCOUNT_COUNT')


def pending_data_deletion_jobs_per_group(ctx):
    groups = dataset_groups(ctx, active_only=True)
    values = []
    seen = set()
    for group_arn in groups:
        items = _inventory(
            ctx, 'list_data_deletion_jobs', 'dataDeletionJobs',
            'dataDeletionJobArn', 'data-deletion-job/', 'data deletion job',
            states=DATA_DELETION_STATES, datasetGroupArn=group_arn)
        for arn, item in items.items():
            if item.get('datasetGroupArn') != group_arn:
                raise NoData('Personalize data deletion job has an inconsistent parent')
            if arn in seen:
                raise NoData('Personalize data deletion job appears in multiple dataset groups')
            seen.add(arn)
        values.append((group_arn,
                       sum(item['status'] == 'PENDING' for item in items.values()),
                       None))
    return maximum(values, 'PersonalizeDatasetGroup',
                   'personalize:ListDatasetGroups+ListDataDeletionJobs')


CHECKS = [
    ('L-14011066', 'Active dataset groups', active_dataset_group_count),
    ('L-052ECD67', 'Active campaigns per dataset group',
     active_campaigns_per_group),
    ('L-D9DD83B7', 'Active solutions per dataset group',
     active_solutions_per_group),
    ('L-4D685096', 'Maximum number of recommenders per dataset group',
     recommenders_per_group),
    ('L-037D5A71', 'Number of schemas', schema_count),
    ('L-B9CFBC8B', 'Active filters per dataset group',
     active_filter_count_per_group),
    ('L-69B72005', 'Pending or In Progress batch inference jobs',
     pending_batch_inference_jobs),
    ('L-9C16B368', 'Pending or In Progress solution versions',
     pending_solution_versions),
    ('L-A11DBE93', 'Pending data deletion jobs per dataset group',
     pending_data_deletion_jobs_per_group),
]


def get_current_quotastatus_personalize(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    return context.run(SERVICE, CHECKS, skip)
