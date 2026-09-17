"""AWS Entity Resolution regional workflow inventories and job concurrency."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

SERVICE = 'entityresolution'
# Listed by the API itself. A QUEUED job is waiting for the quota rather than
# holding it, so counting it would report the limit as exceeded by design.
RUNNING = 'RUNNING'
JOB_STATES = {'RUNNING', 'SUCCEEDED', 'FAILED', 'QUEUED'}
RESOLUTION_TYPES = {'RULE_MATCHING', 'ML_MATCHING', 'PROVIDER'}


def count(ctx, method, key):
    return dict(usage=len(ctx.call(SERVICE, method, key)), source=f'entityresolution:{method}', method='ACCOUNT_COUNT')


def _workflows(ctx, method):
    for summary in ctx.call(SERVICE, method, 'workflowSummaries'):
        name = summary.get('workflowName')
        if not isinstance(name, str) or not name:
            raise NoData('Entity Resolution workflow is missing its name')
        yield name, summary


def _running(ctx, method, names):
    usage = 0
    for name in names:
        for job in ctx.call(SERVICE, method, 'jobs', workflowName=name):
            status = job.get('status')
            if status not in JOB_STATES:
                raise NoData('Entity Resolution job has an unknown status')
            usage += status == RUNNING
    return usage


def matching_jobs(ctx, resolution=None):
    """The provider quota is a sub-limit of the matching one, not a sibling.

    ListMatchingWorkflows states each workflow's resolution type, so the
    provider-service jobs are told apart without reading any workflow detail.
    """
    names = []
    for name, summary in _workflows(ctx, 'list_matching_workflows'):
        kind = summary.get('resolutionType')
        if kind not in RESOLUTION_TYPES:
            raise NoData('Entity Resolution workflow has an unknown resolution type')
        if resolution is None or kind == resolution:
            names.append(name)
    return dict(usage=_running(ctx, 'list_matching_jobs', names),
                source='entityresolution:ListMatchingWorkflows+ListMatchingJobs',
                method='ACCOUNT_SUM')


def id_mapping_jobs(ctx):
    names = [name for name, _summary in _workflows(ctx, 'list_id_mapping_workflows')]
    return dict(usage=_running(ctx, 'list_id_mapping_jobs', names),
                source='entityresolution:ListIdMappingWorkflows+ListIdMappingJobs',
                method='ACCOUNT_SUM')


CHECKS = [
    ('L-60DAF647', 'Matching workflows', lambda ctx: count(ctx, 'list_matching_workflows', 'workflowSummaries')),
    ('L-C5A3094C', 'ID mapping workflows', lambda ctx: count(ctx, 'list_id_mapping_workflows', 'workflowSummaries')),
    ('L-FBA1B7BB', 'ID namespaces', lambda ctx: count(ctx, 'list_id_namespaces', 'idNamespaceSummaries')),
    ('L-00E43259', 'Schema mappings', lambda ctx: count(ctx, 'list_schema_mappings', 'schemaList')),
    ('L-6FC8FD6D', 'Concurrent matching jobs', matching_jobs),
    ('L-0A2F654F', 'Concurrent ID mapping jobs', id_mapping_jobs),
    ('L-06117805', 'Concurrent provider service matching jobs',
     lambda ctx: matching_jobs(ctx, resolution='PROVIDER')),
]


def get_current_quotastatus_entityresolution(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'entityresolution' for service, _ in context.quotas): return []
    return context.run('entityresolution', CHECKS, skip)
