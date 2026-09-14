from unittest.mock import Mock

import pytest

from modules.qmchecks import personalize
from modules.qmcore.aws import NoData
from modules.qmchecks.sagemaker_resources import CHECKS as SAGEMAKER_CHECKS


ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def arn(kind, name):
    return f'arn:aws:personalize:{REGION}:{ACCOUNT}:{kind}/{name}'


class Context:
    account = ACCOUNT
    region = REGION

    def __init__(self, responses):
        self.responses = responses

    def call(self, service, method, key, **kwargs):
        assert service == 'personalize'
        return self.responses.get((method, tuple(sorted(kwargs.items()))), [])


def item(kind, name, status='ACTIVE', **extra):
    fields = {
        'dataset-group': 'datasetGroupArn',
        'solution': 'solutionArn',
        'campaign': 'campaignArn',
        'recommender': 'recommenderArn',
        'schema': 'schemaArn',
        'filter': 'filterArn',
        'batch-inference-job': 'batchInferenceJobArn',
        'data-deletion-job': 'dataDeletionJobArn',
    }
    result = {fields[kind]: arn(kind, name), **extra}
    if status is not None:
        result['status'] = status
    return result


def test_personalize_resource_and_job_counts():
    g1, g2 = arn('dataset-group', 'one'), arn('dataset-group', 'two')
    s1, s2, s3 = (arn('solution', name) for name in ('one', 'two', 'three'))
    responses = {
        ('list_dataset_groups', ()): [
            item('dataset-group', 'one'), item('dataset-group', 'two'),
            item('dataset-group', 'failed', 'CREATE FAILED')],
        ('list_solutions', (('datasetGroupArn', g1),)): [
            item('solution', 'one'), item('solution', 'two'),
            item('solution', 'failed', 'CREATE FAILED')],
        ('list_solutions', (('datasetGroupArn', g2),)): [item('solution', 'three')],
        ('list_campaigns', (('solutionArn', s1),)): [
            item('campaign', 'one'), item('campaign', 'deleted', 'DELETE PENDING')],
        ('list_campaigns', (('solutionArn', s2),)): [item('campaign', 'two')],
        ('list_campaigns', (('solutionArn', s3),)): [item('campaign', 'three')],
        ('list_recommenders', (('datasetGroupArn', g1),)): [
            item('recommender', 'one', datasetGroupArn=g1),
            item('recommender', 'two', 'INACTIVE', datasetGroupArn=g1)],
        ('list_recommenders', (('datasetGroupArn', g2),)): [
            item('recommender', 'three', datasetGroupArn=g2)],
        ('list_schemas', ()): [
            item('schema', 'one', None), item('schema', 'two', None)],
        ('list_filters', (('datasetGroupArn', g1),)): [
            item('filter', 'one', datasetGroupArn=g1),
            item('filter', 'two', datasetGroupArn=g1)],
        ('list_filters', (('datasetGroupArn', g2),)): [
            item('filter', 'failed', 'CREATE FAILED', datasetGroupArn=g2)],
        ('list_batch_inference_jobs', ()): [
            item('batch-inference-job', 'one', 'PENDING'),
            item('batch-inference-job', 'two', 'IN PROGRESS'),
            item('batch-inference-job', 'done')],
        ('list_solution_versions', ()): [
            {'solutionVersionArn': f'{s1}/1', 'status': 'CREATE PENDING'},
            {'solutionVersionArn': f'{s2}/1', 'status': 'CREATE IN_PROGRESS'},
            {'solutionVersionArn': f'{s3}/1', 'status': 'CREATE STOPPED'}],
        ('list_data_deletion_jobs', (('datasetGroupArn', g1),)): [
            item('data-deletion-job', 'one', 'PENDING', datasetGroupArn=g1),
            item('data-deletion-job', 'done', 'COMPLETED', datasetGroupArn=g1)],
        ('list_data_deletion_jobs', (('datasetGroupArn', g2),)): [
            item('data-deletion-job', 'two', 'PENDING', datasetGroupArn=g2),
            item('data-deletion-job', 'three', 'PENDING', datasetGroupArn=g2)],
    }
    ctx = Context(responses)
    values = [fn(ctx) for _, _, fn in personalize.CHECKS]
    assert [value['usage'] for value in values] == [2] * 9
    assert values[1]['method'] == 'PER_RESOURCE_MAX'
    assert values[1]['resource_id'] == g1
    assert values[6]['method'] == 'ACCOUNT_COUNT'


@pytest.mark.parametrize(('function', 'method', 'value'), [
    (personalize.active_dataset_group_count, 'list_dataset_groups',
     item('dataset-group', 'bad', 'UNKNOWN')),
    (personalize.pending_batch_inference_jobs, 'list_batch_inference_jobs',
     item('batch-inference-job', 'bad', 'UNKNOWN')),
    (personalize.pending_solution_versions, 'list_solution_versions',
     {'solutionVersionArn': f"{arn('solution', 'one')}/1", 'status': 'UNKNOWN'}),
])
def test_personalize_rejects_unknown_states(function, method, value):
    with pytest.raises(NoData, match='unknown state'):
        function(Context({(method, ()): [value]}))


def test_personalize_rejects_inconsistent_arn():
    bad = item('schema', 'one', None)
    bad['schemaArn'] = bad['schemaArn'].replace(REGION, 'us-east-1')
    with pytest.raises(NoData, match='inconsistent ARN'):
        personalize.schema_count(Context({('list_schemas', ()): [bad]}))


def test_personalize_rejects_changed_duplicate():
    one = item('batch-inference-job', 'one', 'PENDING')
    changed = {**one, 'status': 'ACTIVE'}
    with pytest.raises(NoData, match='changed during pagination'):
        personalize.pending_batch_inference_jobs(Context({
            ('list_batch_inference_jobs', ()): [one, changed]}))


@pytest.mark.parametrize(('function', 'method', 'kind', 'status'), [
    (personalize.recommenders_per_group, 'list_recommenders',
     'recommender', 'ACTIVE'),
    (personalize.active_filter_count_per_group, 'list_filters',
     'filter', 'ACTIVE'),
    (personalize.pending_data_deletion_jobs_per_group, 'list_data_deletion_jobs',
     'data-deletion-job', 'PENDING'),
])
def test_personalize_rejects_inconsistent_parent(function, method, kind, status):
    group = arn('dataset-group', 'one')
    responses = {
        ('list_dataset_groups', ()): [item('dataset-group', 'one')],
        (method, (('datasetGroupArn', group),)): [
            item(kind, 'one', status,
                 datasetGroupArn=arn('dataset-group', 'other'))],
    }
    with pytest.raises(NoData, match='inconsistent parent'):
        function(Context(responses))


def test_sagemaker_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}], [{}, {}], [{}], [{}, {}, {}]]
    assert [fn(ctx)['usage'] for _, _, fn in SAGEMAKER_CHECKS] == [1, 2, 1, 3]
