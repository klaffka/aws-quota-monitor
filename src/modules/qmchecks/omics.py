"""Amazon Omics store, run, job and share quotas.

Concurrency quotas count only the work still in flight: a completed run, task
or import job releases its capacity, so every such check filters on status.
"""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

OMICS = 'omics'
RUN_STATES = {'PENDING', 'STARTING', 'RUNNING', 'STOPPING', 'COMPLETED', 'DELETED',
              'CANCELLED', 'FAILED'}
ACTIVE_RUN_STATES = {'PENDING', 'STARTING', 'RUNNING', 'STOPPING'}
TASK_STATES = {'PENDING', 'STARTING', 'RUNNING', 'STOPPING', 'COMPLETED', 'CANCELLED',
               'FAILED'}
ACTIVE_TASK_STATES = {'PENDING', 'STARTING', 'RUNNING', 'STOPPING'}
STORAGE_TYPES = {'STATIC', 'DYNAMIC'}
STORE_JOB_STATES = {'SUBMITTED', 'IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'FAILED',
                    'COMPLETED_WITH_FAILURES'}
READ_SET_JOB_STATES = STORE_JOB_STATES | {'CANCELLING'}
RUNNING_JOB_STATES = {'SUBMITTED', 'IN_PROGRESS', 'CANCELLING'}
SHARE_TYPES = {'VARIANT_STORE', 'ANNOTATION_STORE', 'WORKFLOW'}


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call(OMICS, method, key)), source=f'omics:{method}',
                method='ACCOUNT_COUNT')


def runs(ctx):
    found = []
    for run in ctx.call(OMICS, 'list_runs', 'items'):
        status = run.get('status')
        if status is not None and status not in RUN_STATES:
            raise NoData('Omics run has an unknown status')
        identity = run.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Omics run is missing its identity')
        storage = run.get('storageType')
        if storage is not None and storage not in STORAGE_TYPES:
            raise NoData('Omics run has an unknown storage type')
        found.append(run)
    return found


def stored_runs(ctx):
    """A deleted run no longer occupies the account's run history."""
    usage = sum(run.get('status') != 'DELETED' for run in runs(ctx))
    return dict(usage=usage, source='omics:ListRuns', method='ACCOUNT_COUNT')


def _active_runs(ctx, storage=None):
    return [run for run in runs(ctx)
            if run.get('status') in ACTIVE_RUN_STATES
            and (storage is None or run.get('storageType') == storage)]


def _runs_with_storage(storage):
    return lambda ctx: dict(usage=len(_active_runs(ctx, storage)),
                            source='omics:ListRuns', method='ACCOUNT_COUNT')


def _active_tasks(ctx):
    """Yield every task that an unfinished run is still running."""
    for run in _active_runs(ctx):
        for task in ctx.call(OMICS, 'list_run_tasks', 'items', id=run['id']):
            status = task.get('status')
            if status is not None and status not in TASK_STATES:
                raise NoData('Omics run task has an unknown status')
            if status in ACTIVE_TASK_STATES:
                yield run['id'], task


def tasks_per_run(ctx):
    counts = Counter(run for run, _ in _active_tasks(ctx))
    return maximum(((run, count, None) for run, count in counts.items()),
                   'OmicsRun', 'omics:ListRuns+ListRunTasks')


def active_gpus(ctx):
    usage = 0
    for _, task in _active_tasks(ctx):
        gpus = task.get('gpus')
        if gpus is None:
            continue
        if not isinstance(gpus, int) or isinstance(gpus, bool) or gpus < 0:
            raise NoData('Omics run task has an invalid GPU count')
        usage += gpus
    return dict(usage=usage, source='omics:ListRuns+ListRunTasks',
                method='ACCOUNT_COUNT')


def _children_per_store(store_method, store_key, child_method, child_key,
                        parameter, resource_type):
    """Count what each store holds, reported as the fullest store."""
    def check(ctx):
        values = []
        for store in ctx.call(OMICS, store_method, store_key):
            identity = store.get('id')
            if not isinstance(identity, str) or not identity:
                raise NoData('Omics store is missing its identity')
            children = ctx.call(OMICS, child_method, child_key,
                                **{parameter: identity})
            values.append((identity, len(children), None))
        return maximum(values, resource_type, f'omics:{store_method}+{child_method}')
    return check


def annotation_store_versions(ctx):
    values = []
    for store in ctx.call(OMICS, 'list_annotation_stores', 'annotationStores'):
        name = store.get('name')
        if not isinstance(name, str) or not name:
            raise NoData('Omics annotation store is missing its name')
        versions = ctx.call(OMICS, 'list_annotation_store_versions',
                            'annotationStoreVersions', name=name)
        values.append((name, len(versions), None))
    return maximum(values, 'OmicsAnnotationStore',
                   'omics:ListAnnotationStores+ListAnnotationStoreVersions')


def shares(ctx, resource_type):
    """Group the account's own shares by the resource they expose."""
    counts = Counter()
    for share in ctx.call(OMICS, 'list_shares', 'shares', resourceOwner='SELF',
                          filter={'type': [resource_type]}):
        arn = share.get('resourceArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Omics share is missing its resource')
        counts[arn] += 1
    return counts


def _shares_per_resource(resource_type, label):
    def check(ctx):
        counts = shares(ctx, resource_type)
        return maximum(((arn, count, None) for arn, count in counts.items()),
                       label, 'omics:ListShares')
    return check


def _running(entries, states, subject):
    usage = 0
    for entry in entries:
        status = entry.get('status')
        if status is not None and status not in states:
            raise NoData(f'Omics {subject} has an unknown status')
        usage += status in RUNNING_JOB_STATES
    return usage


def store_import_jobs(ctx):
    """Variant and annotation store imports share one concurrency quota."""
    usage = _running(ctx.call(OMICS, 'list_variant_import_jobs', 'variantImportJobs'),
                     STORE_JOB_STATES, 'variant import job')
    usage += _running(ctx.call(OMICS, 'list_annotation_import_jobs',
                               'annotationImportJobs'),
                      STORE_JOB_STATES, 'annotation import job')
    return dict(usage=usage,
                source='omics:ListVariantImportJobs+ListAnnotationImportJobs',
                method='ACCOUNT_COUNT')


def _jobs_per_store(store_method, store_key, job_method, job_key, parameter, subject):
    def check(ctx):
        usage = 0
        for store in ctx.call(OMICS, store_method, store_key):
            identity = store.get('id')
            if not isinstance(identity, str) or not identity:
                raise NoData('Omics store is missing its identity')
            usage += _running(ctx.call(OMICS, job_method, job_key,
                                       **{parameter: identity}),
                              READ_SET_JOB_STATES, subject)
        return dict(usage=usage, source=f'omics:{store_method}+{job_method}',
                    method='ACCOUNT_COUNT')
    return check


def sequence_and_reference_imports(ctx):
    sequence = _jobs_per_store('list_sequence_stores', 'sequenceStores',
                               'list_read_set_import_jobs', 'importJobs',
                               'sequenceStoreId', 'read set import job')(ctx)
    reference = _jobs_per_store('list_reference_stores', 'referenceStores',
                                'list_reference_import_jobs', 'importJobs',
                                'referenceStoreId', 'reference import job')(ctx)
    return dict(usage=sequence['usage'] + reference['usage'],
                source='omics:ListReadSetImportJobs+ListReferenceImportJobs',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-7CAE62CF', 'Workflows - Maximum workflows',
     lambda ctx: resource_count(ctx, 'list_workflows', 'items')),
    ('L-BFFBB2FD', 'Storage - Maximum sequence stores',
     lambda ctx: resource_count(ctx, 'list_sequence_stores', 'sequenceStores')),
    ('L-899DA104', 'Analytics - Maximum variant stores',
     lambda ctx: resource_count(ctx, 'list_variant_stores', 'variantStores')),
    ('L-01A419C5', 'Analytics - Maximum annotation stores',
     lambda ctx: resource_count(ctx, 'list_annotation_stores', 'annotationStores')),
    ('L-D91CDC5E', 'Configurations - Maximum configurations',
     lambda ctx: resource_count(ctx, 'list_configurations', 'items')),
    ('L-C9679DBC', 'Workflows - Maximum runs (active or inactive)', stored_runs),
    ('L-A30FD31B',
     'Workflows - Maximum concurrent active runs using static run storage',
     _runs_with_storage('STATIC')),
    ('L-BE38079A',
     'Workflows - Maximum concurrent active runs using dynamic run storage',
     _runs_with_storage('DYNAMIC')),
    ('L-25504C8C', 'Workflows - Maximum concurrent tasks per run', tasks_per_run),
    ('L-AFB19B96', 'Workflows - Maximum active GPUs', active_gpus),
    ('L-BE766427', 'Storage - Maximum read sets per sequence store',
     _children_per_store('list_sequence_stores', 'sequenceStores', 'list_read_sets',
                         'readSets', 'sequenceStoreId', 'OmicsSequenceStore')),
    ('L-F34A3FC2', 'Storage - Maximum references per reference store',
     _children_per_store('list_reference_stores', 'referenceStores', 'list_references',
                         'references', 'referenceStoreId', 'OmicsReferenceStore')),
    ('L-186D3DEB', 'Analytics - Maximum versions per annotation store',
     annotation_store_versions),
    ('L-242998FB', 'Analytics - Maximum shares per variant store',
     _shares_per_resource('VARIANT_STORE', 'OmicsVariantStore')),
    ('L-E787EB79', 'Analytics - Maximum shares per annotation store',
     _shares_per_resource('ANNOTATION_STORE', 'OmicsAnnotationStore')),
    ('L-4E5B34A1', 'Workflows - Maximum shares per workflow',
     _shares_per_resource('WORKFLOW', 'OmicsWorkflow')),
    ('L-876AD0A2',
     'Analytics - Maximum concurrent variant or annotation store import jobs',
     store_import_jobs),
    ('L-F57A8D18',
     'Storage - Maximum concurrent sequence or reference store import jobs',
     sequence_and_reference_imports),
    ('L-473E274D',
     'Storage - Maximum concurrent sequence and reference store export jobs',
     _jobs_per_store('list_sequence_stores', 'sequenceStores',
                     'list_read_set_export_jobs', 'exportJobs', 'sequenceStoreId',
                     'read set export job')),
    ('L-911E26A1', 'Storage - Maximum concurrent read set activation jobs',
     _jobs_per_store('list_sequence_stores', 'sequenceStores',
                     'list_read_set_activation_jobs', 'activationJobs',
                     'sequenceStoreId', 'read set activation job')),
]


def get_current_quotastatus_omics(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'omics' for service, _ in context.quotas):
        return []
    return context.run('omics', CHECKS, skip)
