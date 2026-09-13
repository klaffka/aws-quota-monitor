"""Amazon Forecast regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('forecast', method, key)), source=f'forecast:{method}', method='ACCOUNT_COUNT')


def predictors(ctx, auto=None):
    items = ctx.call('forecast', 'list_predictors', 'Predictors')
    if auto is None:
        return items
    return [item for item in items if bool(item.get('IsAutoPredictor')) is auto]


CHECKS = [
    ('L-9C589A93', 'Maximum number of predictors',
     lambda ctx: dict(usage=len(predictors(ctx)), source='forecast:ListPredictors', method='ACCOUNT_COUNT')),
    ('L-FBF2B427', 'Maximum number of AutoPredictors',
     lambda ctx: dict(usage=len(predictors(ctx, True)), source='forecast:ListPredictors', method='ACCOUNT_COUNT')),
    ('L-5054D782', 'Maximum number of dataset groups',
     lambda ctx: resource_count(ctx, 'list_dataset_groups', 'DatasetGroups')),
    ('L-D613D53B', 'Maximum number of datasets',
     lambda ctx: resource_count(ctx, 'list_datasets', 'Datasets')),
    ('L-884F7F75', 'Maximum number of forecasts',
     lambda ctx: resource_count(ctx, 'list_forecasts', 'Forecasts')),
    ('L-F58E51A9', 'Maximum number of Explainabilities',
     lambda ctx: resource_count(ctx, 'list_explainabilities', 'Explainabilities')),
    ('L-235B11D6', 'Maximum number of What-if Analyses',
     lambda ctx: resource_count(ctx, 'list_what_if_analyses', 'WhatIfAnalyses')),
    ('L-762142D9', 'Maximum number of What-if Forecasts',
     lambda ctx: resource_count(ctx, 'list_what_if_forecasts', 'WhatIfForecasts')),
    ('L-561FC25E', 'Maximum number of forecast export jobs',
     lambda ctx: resource_count(ctx, 'list_forecast_export_jobs', 'ForecastExportJobs')),
    ('L-928BCA42', 'Maximum number of Explainability exports',
     lambda ctx: resource_count(ctx, 'list_explainability_exports', 'ExplainabilityExports')),
    ('L-6AD28BD9', 'Maximum number of What-if Forecast exports',
     lambda ctx: resource_count(ctx, 'list_what_if_forecast_exports', 'WhatIfForecastExports')),
    ('L-E1AC300F', 'Maximum number of predictor backtest export jobs',
     lambda ctx: resource_count(ctx, 'list_predictor_backtest_exports', 'PredictorBacktestExportJobs')),
]


def get_current_quotastatus_forecast(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'forecast' for service, _ in context.quotas):
        return []
    return context.run('forecast', CHECKS, skip)
