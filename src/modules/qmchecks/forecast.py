"""Amazon Forecast resource, parallel task, dataset and predictor quotas.

The column and horizon quotas read as bounds on one dataset or request, but the
describe operations report both as resolved configuration: a dataset's schema
lists its columns and a predictor states the horizon it was built for, so they
are inventories rather than bounds and are measured here.

The row and S3 file quotas really do bound the data behind a dataset, which no
operation reports. The `QueryForecast` parallelism is a request rate, and tags
per resource would need a tag listing for every resource in the account.

`Maximum number of backtest windows` is left open on purpose. It lives in
`EvaluationParameters`, which `CreatePredictor` treats as optional and defaults
to one window; whether a describe echoes that default for a predictor built
without it is not something this catalog can settle, and counting only the
predictors that state it would report a confident undercount for every account
that took the default.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

FORECAST = 'forecast'
# Each of the three dataset types has a column quota of its own, so a type the
# SDK does not name belongs to a quota that is not measured here at all.
DATASET_TYPES = {'TARGET_TIME_SERIES', 'RELATED_TIME_SERIES', 'ITEM_METADATA'}
# Forecast reports lifecycle statuses as <VERB>_<STATE>; a resource is still
# being built while its state is pending or in progress.
RUNNING_SUFFIXES = ('_PENDING', '_IN_PROGRESS')


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call(FORECAST, method, key)), source=f'forecast:{method}', method='ACCOUNT_COUNT')


def _running(items, subject):
    usage = 0
    for item in items:
        status = item.get('Status')
        if not isinstance(status, str) or not status:
            raise NoData(f'Forecast {subject} has no status')
        usage += status.endswith(RUNNING_SUFFIXES)
    return usage


def _parallel_tasks(method, key, subject, predicate=None):
    """Count the resources of one kind that are still being created."""
    def check(ctx):
        items = ctx.call(FORECAST, method, key)
        if predicate is not None:
            items = [item for item in items if predicate(item)]
        return dict(usage=_running(items, subject), source=f'forecast:{method}',
                    method='ACCOUNT_COUNT')
    return check


def datasets_per_dataset_group(ctx):
    values = []
    for group in ctx.call(FORECAST, 'list_dataset_groups', 'DatasetGroups'):
        arn = group.get('DatasetGroupArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Forecast dataset group is missing its ARN')
        detail = ctx.call(FORECAST, 'describe_dataset_group', DatasetGroupArn=arn)
        datasets = detail.get('DatasetArns')
        if not isinstance(datasets, list):
            raise NoData('Forecast dataset group has no datasets')
        values.append((arn, len(datasets), None))
    return maximum(values, 'ForecastDatasetGroup', 'forecast:DescribeDatasetGroup')


def predictors(ctx, auto=None):
    items = ctx.call(FORECAST, 'list_predictors', 'Predictors')
    if auto is None:
        return items
    return [item for item in items if bool(item.get('IsAutoPredictor')) is auto]


def _identity(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Forecast {subject} is missing its identity')
    return value


def columns_per_dataset(dataset_type):
    """Measure the widest schema among the datasets of one type."""
    def check(ctx):
        values = []
        for summary in ctx.call(FORECAST, 'list_datasets', 'Datasets'):
            arn = _identity(summary, 'DatasetArn', 'dataset')
            kind = summary.get('DatasetType')
            if kind not in DATASET_TYPES:
                raise NoData('Forecast dataset has an unknown dataset type')
            if kind != dataset_type:
                continue
            detail = ctx.call(FORECAST, 'describe_dataset', DatasetArn=arn)
            attributes = (detail.get('Schema') or {}).get('Attributes')
            if not isinstance(attributes, list):
                raise NoData('Forecast dataset has no schema')
            values.append((arn, len(attributes), None))
        return maximum(values, 'ForecastDataset', 'forecast:DescribeDataset')
    return check


def forecast_horizon(ctx):
    """An auto predictor answers a different describe than a classic one."""
    values = []
    for summary in predictors(ctx):
        arn = _identity(summary, 'PredictorArn', 'predictor')
        method = ('describe_auto_predictor' if summary.get('IsAutoPredictor')
                  else 'describe_predictor')
        detail = ctx.call(FORECAST, method, PredictorArn=arn)
        horizon = detail.get('ForecastHorizon')
        if not isinstance(horizon, int):
            raise NoData('Forecast predictor states no horizon')
        values.append((arn, horizon, None))
    return maximum(values, 'ForecastPredictor',
                   'forecast:DescribePredictor+DescribeAutoPredictor')


def forecasts_per_export(ctx):
    """The export summary names the forecasts it exports, so no describe runs."""
    values = []
    for summary in ctx.call(FORECAST, 'list_what_if_forecast_exports',
                            'WhatIfForecastExports'):
        arn = _identity(summary, 'WhatIfForecastExportArn', 'what-if forecast export')
        forecasts = summary.get('WhatIfForecastArns')
        if not isinstance(forecasts, list) or not forecasts:
            raise NoData('Forecast what-if export names no forecast')
        values.append((arn, len(forecasts), None))
    return maximum(values, 'ForecastWhatIfForecastExport',
                   'forecast:ListWhatIfForecastExports')


CHECKS = [
    ('L-9C589A93', 'Maximum number of predictors',
     lambda ctx: dict(usage=len(predictors(ctx)), source='forecast:ListPredictors', method='ACCOUNT_COUNT')),
    ('L-FBF2B427', 'The maximum number of AutoPredictors',
     lambda ctx: dict(usage=len(predictors(ctx, True)), source='forecast:ListPredictors', method='ACCOUNT_COUNT')),
    ('L-5054D782', 'Maximum number of dataset groups',
     lambda ctx: resource_count(ctx, 'list_dataset_groups', 'DatasetGroups')),
    ('L-D613D53B', 'Maximum number of datasets',
     lambda ctx: resource_count(ctx, 'list_datasets', 'Datasets')),
    ('L-884F7F75', 'Maximum number of forecasts',
     lambda ctx: resource_count(ctx, 'list_forecasts', 'Forecasts')),
    ('L-F58E51A9', 'Maximum number of Explainabilities',
     lambda ctx: resource_count(ctx, 'list_explainabilities', 'Explainabilities')),
    ('L-235B11D6', 'The maximum number of What-if Analyses',
     lambda ctx: resource_count(ctx, 'list_what_if_analyses', 'WhatIfAnalyses')),
    ('L-762142D9', 'The maximum number of What-if Forecasts',
     lambda ctx: resource_count(ctx, 'list_what_if_forecasts', 'WhatIfForecasts')),
    ('L-561FC25E', 'Maximum number of forecast export jobs',
     lambda ctx: resource_count(ctx, 'list_forecast_export_jobs', 'ForecastExportJobs')),
    ('L-928BCA42', 'Maximum number of Explainability exports',
     lambda ctx: resource_count(ctx, 'list_explainability_exports', 'ExplainabilityExports')),
    ('L-6AD28BD9', 'The maximum number of What-if Forecast Exports',
     lambda ctx: resource_count(ctx, 'list_what_if_forecast_exports', 'WhatIfForecastExports')),
    ('L-E1AC300F', 'Maximum number of predictor backtest export jobs',
     lambda ctx: resource_count(ctx, 'list_predictor_backtest_export_jobs', 'PredictorBacktestExportJobs')),
    ('L-1306EC42', 'Maximum number of dataset import jobs',
     lambda ctx: resource_count(ctx, 'list_dataset_import_jobs', 'DatasetImportJobs')),
    ('L-D71794C7', 'Maximum number of datasets in a dataset group',
     datasets_per_dataset_group),
    ('L-407BD890', 'Maximum parallel running CreateDatasetImportJob tasks',
     _parallel_tasks('list_dataset_import_jobs', 'DatasetImportJobs',
                     'dataset import job')),
    ('L-3154C698', 'Maximum parallel running CreatePredictor tasks',
     _parallel_tasks('list_predictors', 'Predictors', 'predictor',
                     lambda item: not item.get('IsAutoPredictor'))),
    ('L-24281831', 'Maximum parallel running CreateAutoPredictor tasks',
     _parallel_tasks('list_predictors', 'Predictors', 'predictor',
                     lambda item: bool(item.get('IsAutoPredictor')))),
    ('L-10DDC31D', 'Maximum parallel running CreateForecast tasks',
     _parallel_tasks('list_forecasts', 'Forecasts', 'forecast')),
    ('L-02D995E1', 'Maximum parallel running CreateForecastExportJob tasks',
     _parallel_tasks('list_forecast_export_jobs', 'ForecastExportJobs',
                     'forecast export job')),
    ('L-A6F48898', 'Maximum parallel running CreateExplainability tasks',
     _parallel_tasks('list_explainabilities', 'Explainabilities', 'explainability')),
    ('L-143E66E3', 'Maximum parallel running CreateExplainabilityExport tasks',
     _parallel_tasks('list_explainability_exports', 'ExplainabilityExports',
                     'explainability export')),
    ('L-C4147F5F', 'Maximum parallel running CreatePredictorBacktestExportJob tasks',
     _parallel_tasks('list_predictor_backtest_export_jobs', 'PredictorBacktestExportJobs',
                     'predictor backtest export job')),
    ('L-3DED4AA6', 'Maximum parallel running CreateWhatIfAnalysis tasks',
     _parallel_tasks('list_what_if_analyses', 'WhatIfAnalyses', 'what-if analysis')),
    ('L-5EC8963B', 'Maximum parallel running CreateWhatIfForecast tasks',
     _parallel_tasks('list_what_if_forecasts', 'WhatIfForecasts',
                     'what-if forecast')),
    ('L-B50F9B6C', 'Maximum parallel running CreateWhatIfForecastExport tasks',
     _parallel_tasks('list_what_if_forecast_exports', 'WhatIfForecastExports',
                     'what-if forecast export')),
    ('L-9FD32A46', 'Maximum number of columns in a target time series dataset',
     columns_per_dataset('TARGET_TIME_SERIES')),
    ('L-3D30706E', 'Maximum number of columns in a related time series dataset',
     columns_per_dataset('RELATED_TIME_SERIES')),
    ('L-F37CCDC6', 'Maximum number of columns in an item metadata dataset',
     columns_per_dataset('ITEM_METADATA')),
    ('L-57E6FE87', 'Maximum forecast horizon', forecast_horizon),
    ('L-50FA8F07',
     'The maximum number of What-if Forecasts in a CreateWhatIfForecastExport task',
     forecasts_per_export),
]


def get_current_quotastatus_forecast(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'forecast' for service, _ in context.quotas):
        return []
    return context.run('forecast', CHECKS, skip)
