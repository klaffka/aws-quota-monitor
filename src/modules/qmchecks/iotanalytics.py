"""AWS IoT Analytics regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-0AED1111', 'Pipelines per account',
     lambda c: dict(usage=len(c.call('iotanalytics', 'list_pipelines', 'pipelineSummaries')),
                    source='iotanalytics:ListPipelines', method='ACCOUNT_COUNT')),
    ('L-321F3834', 'Channels per account',
     lambda c: dict(usage=len(c.call('iotanalytics', 'list_channels', 'channelSummaries')),
                    source='iotanalytics:ListChannels', method='ACCOUNT_COUNT')),
    ('L-4BFEAE82', 'Data sets per account',
     lambda c: dict(usage=len(c.call('iotanalytics', 'list_datasets', 'datasetSummaries')),
                    source='iotanalytics:ListDatasets', method='ACCOUNT_COUNT')),
    ('L-86CFEC61', 'Data stores per account',
     lambda c: dict(usage=len(c.call('iotanalytics', 'list_datastores', 'datastoreSummaries')),
                    source='iotanalytics:ListDatastores', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_iotanalytics(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotanalytics' for service, _ in context.quotas):
        return []
    return context.run('iotanalytics', CHECKS, skip)
