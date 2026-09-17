"""SageMaker instance-type usage for the families AWS publishes no metric for."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import sagemaker_instances as instances
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=timezone.utc)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'sagemaker', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in instances.CHECKS if quota == code)


def training_summary(name, warm_pool=None):
    summary = {'TrainingJobName': name, 'TrainingJobArn': f'arn:tj/{name}',
               'CreationTime': MOMENT, 'TrainingJobStatus': 'InProgress'}
    if warm_pool:
        summary['WarmPoolStatus'] = {'Status': warm_pool}
    return summary


def training_detail(name, instance_type, count, *, spot=False, warm_pool=None, groups=None):
    resource = {'VolumeSizeInGB': 30}
    if groups:
        resource['InstanceGroups'] = [
            {'InstanceType': t, 'InstanceCount': c, 'InstanceGroupName': f'g{i}'}
            for i, (t, c) in enumerate(groups)]
    else:
        resource['InstanceType'] = instance_type
        resource['InstanceCount'] = count
    detail = {'TrainingJobName': name, 'TrainingJobArn': f'arn:tj/{name}',
              'ModelArtifacts': {'S3ModelArtifacts': 's3://b/k'},
              'TrainingJobStatus': 'InProgress', 'SecondaryStatus': 'Training',
              'AlgorithmSpecification': {'TrainingInputMode': 'File'},
              'ResourceConfig': resource, 'CreationTime': MOMENT,
              'StoppingCondition': {'MaxRuntimeInSeconds': 600},
              'EnableManagedSpotTraining': spot}
    if warm_pool:
        detail['WarmPoolStatus'] = {'Status': warm_pool}
    return detail


def test_on_demand_and_spot_training_hold_separate_quotas():
    """AWS bounds managed spot capacity apart from on-demand capacity."""
    ctx = context('L-D438008E')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_training_jobs', {'TrainingJobSummaries': [
            training_summary('plain'), training_summary('spot')]},
            {'StatusEquals': 'InProgress'})
        stub.add_response('describe_training_job',
                          training_detail('plain', 'ml.p3.2xlarge', 2),
                          {'TrainingJobName': 'plain'})
        stub.add_response('describe_training_job',
                          training_detail('spot', 'ml.p3.2xlarge', 8, spot=True),
                          {'TrainingJobName': 'spot'})
        result = check('L-D438008E')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_SUM')
        stub.assert_no_pending_responses()


def test_the_spot_quota_counts_only_managed_spot_jobs():
    ctx = context('L-2D4C6493')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_training_jobs', {'TrainingJobSummaries': [
            training_summary('plain'), training_summary('spot')]},
            {'StatusEquals': 'InProgress'})
        stub.add_response('describe_training_job',
                          training_detail('plain', 'ml.p3.2xlarge', 2),
                          {'TrainingJobName': 'plain'})
        stub.add_response('describe_training_job',
                          training_detail('spot', 'ml.p3.2xlarge', 8, spot=True),
                          {'TrainingJobName': 'spot'})
        assert check('L-2D4C6493')(ctx)['usage'] == 8


def test_another_instance_type_does_not_count_towards_this_quota():
    ctx = context('L-D438008E')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_training_jobs',
                          {'TrainingJobSummaries': [training_summary('other')]},
                          {'StatusEquals': 'InProgress'})
        stub.add_response('describe_training_job',
                          training_detail('other', 'ml.p4d.24xlarge', 4),
                          {'TrainingJobName': 'other'})
        assert check('L-D438008E')(ctx)['usage'] == 0


def test_a_heterogeneous_cluster_counts_only_its_matching_groups():
    """A job may state instance groups instead of one type and count."""
    ctx = context('L-558F1246')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_training_jobs',
                          {'TrainingJobSummaries': [training_summary('mixed')]},
                          {'StatusEquals': 'InProgress'})
        stub.add_response('describe_training_job',
                          training_detail('mixed', None, None,
                                          groups=[('ml.p3.8xlarge', 3),
                                                  ('ml.c5.xlarge', 9)]),
                          {'TrainingJobName': 'mixed'})
        assert check('L-558F1246')(ctx)['usage'] == 3


def test_a_resource_configuration_without_a_count_is_reported():
    ctx = context('L-D438008E')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_training_jobs',
                          {'TrainingJobSummaries': [training_summary('bare')]},
                          {'StatusEquals': 'InProgress'})
        detail = training_detail('bare', 'ml.p3.2xlarge', 1)
        del detail['ResourceConfig']['InstanceCount']
        stub.add_response('describe_training_job', detail, {'TrainingJobName': 'bare'})
        with pytest.raises(NoData, match='instance count'):
            check('L-D438008E')(ctx)


def test_only_the_warm_pool_states_that_retain_instances_are_asked_for():
    """A terminated warm pool holds nothing; the other three still do."""
    ctx = context('L-E3709F6E')
    with Stubber(ctx.client('sagemaker')) as stub:
        for status, count in (('Available', 1), ('InUse', 2), ('Reused', 4)):
            stub.add_response('list_training_jobs', {'TrainingJobSummaries': [
                training_summary(status.lower(), warm_pool=status)]},
                {'WarmPoolStatusEquals': status})
            stub.add_response('describe_training_job',
                              training_detail(status.lower(), 'ml.p3.2xlarge', count,
                                              warm_pool=status),
                              {'TrainingJobName': status.lower()})
        assert check('L-E3709F6E')(ctx)['usage'] == 7
        stub.assert_no_pending_responses()


def test_processing_jobs_are_counted_from_their_cluster_configuration():
    ctx = context('L-0323EDB4')
    with Stubber(ctx.client('sagemaker')) as stub:
        stub.add_response('list_processing_jobs', {'ProcessingJobSummaries': [
            {'ProcessingJobName': 'one', 'ProcessingJobArn': 'arn:pj/one',
             'CreationTime': MOMENT, 'ProcessingJobStatus': 'InProgress'}]},
            {'StatusEquals': 'InProgress'})
        stub.add_response('describe_processing_job', {
            'ProcessingJobName': 'one', 'ProcessingJobArn': 'arn:pj/one',
            'ProcessingJobStatus': 'InProgress', 'CreationTime': MOMENT,
            'AppSpecification': {'ImageUri': 'example'},
            'ProcessingResources': {'ClusterConfig': {
                'InstanceCount': 5, 'InstanceType': 'ml.p3.2xlarge',
                'VolumeSizeInGB': 30}}},
            {'ProcessingJobName': 'one'})
        assert check('L-0323EDB4')(ctx)['usage'] == 5
        stub.assert_no_pending_responses()


def test_every_instance_quota_names_a_type_the_catalog_has_no_metric_for():
    """These exist only because AWS publishes no usage metric for ml.p3."""
    import json
    from pathlib import Path
    catalog = json.loads(Path('tests/fixtures/quota-catalog-union.json').read_text(encoding='utf-8'))
    metrics = {q['QuotaCode']: bool(q.get('UsageMetric')) for q in catalog
               if q.get('ServiceCode') == 'sagemaker'}
    published = sorted(code for code, _name, _fn in instances.CHECKS if metrics.get(code))
    assert not published, f'AWS now publishes a metric for these, so drop them: {published}'
