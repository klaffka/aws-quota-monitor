import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import forecast
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

GROUP = 'arn:aws:forecast:eu-central-1:123456789012:dataset-group/retail'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'forecast', 'QuotaCode': code, 'Value': 10}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in forecast.CHECKS if quota == code)


def test_pending_and_in_progress_resources_count_as_parallel_tasks():
    ctx = context('L-10DDC31D')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_forecasts', {'Forecasts': [
            {'ForecastName': 'a', 'Status': 'CREATE_PENDING'},
            {'ForecastName': 'b', 'Status': 'CREATE_IN_PROGRESS'},
            {'ForecastName': 'c', 'Status': 'ACTIVE'},
            {'ForecastName': 'd', 'Status': 'CREATE_FAILED'}]}, {})
        assert check('L-10DDC31D')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_predictor_tasks_separate_autopredictors_from_the_rest():
    predictors = [{'PredictorName': 'a', 'Status': 'CREATE_IN_PROGRESS',
                   'IsAutoPredictor': True},
                  {'PredictorName': 'b', 'Status': 'CREATE_IN_PROGRESS'},
                  {'PredictorName': 'c', 'Status': 'CREATE_PENDING'}]
    for code, expected in (('L-24281831', 1), ('L-3154C698', 2)):
        ctx = context(code)
        with Stubber(ctx.client('forecast')) as stub:
            stub.add_response('list_predictors', {'Predictors': predictors}, {})
            assert check(code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_a_resource_without_a_status_raises_nodata():
    ctx = context('L-10DDC31D')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_forecasts', {'Forecasts': [{'ForecastName': 'a'}]}, {})
        with pytest.raises(NoData, match='no status'):
            check('L-10DDC31D')(ctx)


def test_datasets_are_counted_per_dataset_group():
    ctx = context('L-D71794C7')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_dataset_groups', {'DatasetGroups': [
            {'DatasetGroupArn': GROUP, 'DatasetGroupName': 'retail'}]}, {})
        stub.add_response('describe_dataset_group', {
            'DatasetGroupArn': GROUP, 'DatasetGroupName': 'retail',
            'DatasetArns': ['arn:aws:forecast:::dataset/a',
                            'arn:aws:forecast:::dataset/b']}, {'DatasetGroupArn': GROUP})
        result = forecast.datasets_per_dataset_group(ctx)
        assert (result['usage'], result['resource_id']) == (2, GROUP)
        stub.assert_no_pending_responses()


def test_every_forecast_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'forecast'}
    assert {code for code, _, _ in forecast.CHECKS} <= registered
