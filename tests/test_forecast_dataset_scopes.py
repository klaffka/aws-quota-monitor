"""Forecast scopes that a describe reports as an inventory rather than a bound."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import forecast
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'forecast', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in forecast.CHECKS if quota == code)


def dataset_arn(name):
    return f'arn:aws:forecast:{REGION}:{ACCOUNT}:dataset/{name}'


def predictor_arn(name):
    return f'arn:aws:forecast:{REGION}:{ACCOUNT}:predictor/{name}'


def stub_datasets(stub, datasets, schemas=()):
    """Stub the dataset listing, then a describe for each named dataset.

    ``datasets`` holds ``(name, dataset type)``; ``schemas`` holds
    ``(name, column count)`` for the ones the check goes on to describe.
    """
    stub.add_response('list_datasets', {'Datasets': [
        {'DatasetArn': dataset_arn(name), 'DatasetName': name, 'DatasetType': kind}
        for name, kind in datasets]}, {})
    for name, columns in schemas:
        stub.add_response('describe_dataset', {
            'DatasetArn': dataset_arn(name), 'DatasetName': name,
            'Schema': {'Attributes': [
                {'AttributeName': f'c{index}', 'AttributeType': 'string'}
                for index in range(columns)]}},
            {'DatasetArn': dataset_arn(name)})


@pytest.mark.parametrize('code, kind', [
    ('L-9FD32A46', 'TARGET_TIME_SERIES'),
    ('L-3D30706E', 'RELATED_TIME_SERIES'),
    ('L-F37CCDC6', 'ITEM_METADATA'),
])
def test_each_dataset_type_counts_only_its_own_columns(code, kind):
    """The three column quotas name one dataset type each."""
    ctx = context(code)
    with Stubber(ctx.client('forecast')) as stub:
        stub_datasets(stub,
                      [('target', 'TARGET_TIME_SERIES'),
                       ('related', 'RELATED_TIME_SERIES'),
                       ('items', 'ITEM_METADATA')],
                      schemas=[({'TARGET_TIME_SERIES': 'target',
                                 'RELATED_TIME_SERIES': 'related',
                                 'ITEM_METADATA': 'items'}[kind], 3)])
        result = check(code)(ctx)
        assert result['usage'] == 3
        stub.assert_no_pending_responses()


def test_the_widest_dataset_of_a_type_is_the_one_measured():
    ctx = context('L-9FD32A46')
    with Stubber(ctx.client('forecast')) as stub:
        stub_datasets(stub,
                      [('narrow', 'TARGET_TIME_SERIES'), ('wide', 'TARGET_TIME_SERIES')],
                      schemas=[('narrow', 2), ('wide', 5)])
        result = check('L-9FD32A46')(ctx)
        assert (result['usage'], result['resource_id']) == (5, dataset_arn('wide'))
        stub.assert_no_pending_responses()


def test_an_account_with_no_dataset_of_that_type_counts_as_zero():
    ctx = context('L-F37CCDC6')
    with Stubber(ctx.client('forecast')) as stub:
        stub_datasets(stub, [('target', 'TARGET_TIME_SERIES')])
        assert check('L-F37CCDC6')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_dataset_type_the_sdk_does_not_name_is_reported():
    """A new dataset type would have its own quota; guessing would hide it."""
    ctx = context('L-9FD32A46')
    with Stubber(ctx.client('forecast')) as stub:
        stub_datasets(stub, [('odd', 'GEOLOCATION')])
        with pytest.raises(NoData, match='dataset type'):
            check('L-9FD32A46')(ctx)


def test_a_dataset_without_a_schema_is_reported():
    ctx = context('L-9FD32A46')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_datasets', {'Datasets': [
            {'DatasetArn': dataset_arn('bare'), 'DatasetType': 'TARGET_TIME_SERIES'}]}, {})
        stub.add_response('describe_dataset',
                          {'DatasetArn': dataset_arn('bare'), 'Schema': {}},
                          {'DatasetArn': dataset_arn('bare')})
        with pytest.raises(NoData, match='schema'):
            check('L-9FD32A46')(ctx)


def stub_predictors(stub, predictors):
    """Stub the predictor listing, then the describe each kind answers to."""
    stub.add_response('list_predictors', {'Predictors': [
        {'PredictorArn': predictor_arn(name), 'PredictorName': name,
         'IsAutoPredictor': auto} for name, auto, _ in predictors]}, {})
    for name, auto, horizon in predictors:
        response = {'PredictorArn': predictor_arn(name), 'PredictorName': name}
        if horizon is not None:
            response['ForecastHorizon'] = horizon
        stub.add_response('describe_auto_predictor' if auto else 'describe_predictor',
                          response, {'PredictorArn': predictor_arn(name)})


def test_the_longest_horizon_is_found_across_both_kinds_of_predictor():
    """An auto predictor answers a different describe than a classic one."""
    ctx = context('L-57E6FE87')
    with Stubber(ctx.client('forecast')) as stub:
        stub_predictors(stub, [('classic', False, 24), ('auto', True, 90)])
        result = check('L-57E6FE87')(ctx)
        assert (result['usage'], result['resource_id']) == (90, predictor_arn('auto'))
        stub.assert_no_pending_responses()


def test_an_account_without_predictors_has_no_horizon():
    ctx = context('L-57E6FE87')
    with Stubber(ctx.client('forecast')) as stub:
        stub_predictors(stub, [])
        assert check('L-57E6FE87')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_predictor_that_states_no_horizon_is_reported():
    """Every predictor resolves a horizon, so an absent one is not a zero."""
    ctx = context('L-57E6FE87')
    with Stubber(ctx.client('forecast')) as stub:
        stub_predictors(stub, [('classic', False, None)])
        with pytest.raises(NoData, match='horizon'):
            check('L-57E6FE87')(ctx)


def test_what_if_forecasts_are_counted_from_the_export_listing():
    """The export summary names its forecasts, so no describe is needed."""
    ctx = context('L-50FA8F07')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_what_if_forecast_exports', {
            'WhatIfForecastExports': [
                {'WhatIfForecastExportArn': 'arn:export/one',
                 'WhatIfForecastArns': ['arn:wif/a']},
                {'WhatIfForecastExportArn': 'arn:export/many',
                 'WhatIfForecastArns': ['arn:wif/a', 'arn:wif/b', 'arn:wif/c']}]}, {})
        result = check('L-50FA8F07')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'arn:export/many')
        stub.assert_no_pending_responses()


def test_an_export_naming_no_forecast_is_reported():
    ctx = context('L-50FA8F07')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_what_if_forecast_exports', {
            'WhatIfForecastExports': [
                {'WhatIfForecastExportArn': 'arn:export/empty'}]}, {})
        with pytest.raises(NoData, match='forecast'):
            check('L-50FA8F07')(ctx)
