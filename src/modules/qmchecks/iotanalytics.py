"""AWS IoT Analytics regional resource-count quotas.

botocore no longer ships an `iotanalytics` client; the calls are still
attempted so the checks recover by themselves if the SDK restores the service.
"""
from modules.qmcore.aws import CheckContext, sdk_call, session_from_env

IOTANALYTICS = 'iotanalytics'


def count(ctx, method, key, operation):
    return dict(usage=len(sdk_call(ctx, IOTANALYTICS, method, key)),
                source=f'iotanalytics:{operation}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-0AED1111', 'Pipelines per account',
     lambda ctx: count(ctx, 'list_pipelines', 'pipelineSummaries', 'ListPipelines')),
    ('L-321F3834', 'Channels per account',
     lambda ctx: count(ctx, 'list_channels', 'channelSummaries', 'ListChannels')),
    ('L-4BFEAE82', 'Data sets per account',
     lambda ctx: count(ctx, 'list_datasets', 'datasetSummaries', 'ListDatasets')),
    ('L-86CFEC61', 'Data stores per account',
     lambda ctx: count(ctx, 'list_datastores', 'datastoreSummaries',
                       'ListDatastores')),
]


def get_current_quotastatus_iotanalytics(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == IOTANALYTICS for service, _ in context.quotas):
        return []
    return context.run(IOTANALYTICS, CHECKS, skip)
