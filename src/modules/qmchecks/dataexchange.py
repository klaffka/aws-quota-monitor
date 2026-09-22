"""AWS Data Exchange data set, revision, asset, job and data grant quotas.

The asset size quota bounds one file, `Assets per import job from Amazon S3`
and its siblings bound a single job's input, and `Products per data set` lives
in AWS Marketplace rather than in Data Exchange.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DATAEXCHANGE = 'dataexchange'
ASSET_TYPES = {'S3_SNAPSHOT', 'REDSHIFT_DATA_SHARE', 'API_GATEWAY_API',
               'S3_DATA_ACCESS', 'LAKE_FORMATION_DATA_PERMISSION'}
JOB_STATES = {'WAITING', 'IN_PROGRESS', 'ERROR', 'COMPLETED', 'CANCELLED',
              'TIMED_OUT'}
RUNNING_JOB_STATES = {'WAITING', 'IN_PROGRESS'}
GRANT_STATES = {'PENDING_RECEIVER_ACCEPTANCE', 'ACCEPTED'}
JOB_TYPES = {'IMPORT_ASSETS_FROM_S3', 'IMPORT_ASSET_FROM_SIGNED_URL',
             'EXPORT_ASSETS_TO_S3', 'EXPORT_ASSET_TO_SIGNED_URL',
             'EXPORT_REVISIONS_TO_S3', 'IMPORT_ASSETS_FROM_REDSHIFT_DATA_SHARES',
             'IMPORT_ASSET_FROM_API_GATEWAY_API',
             'CREATE_S3_DATA_ACCESS_FROM_S3_BUCKET',
             'IMPORT_ASSETS_FROM_LAKE_FORMATION_TAG_POLICY'}


def data_sets(ctx):
    found = {}
    for data_set in ctx.call(DATAEXCHANGE, 'list_data_sets', 'DataSets'):
        identity = data_set.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Data Exchange data set is missing its identity')
        if data_set.get('AssetType') not in ASSET_TYPES:
            raise NoData('Data Exchange data set has an unknown asset type')
        found[identity] = data_set
    return found


def revisions(data_set, ctx):
    found = []
    for revision in ctx.call(DATAEXCHANGE, 'list_data_set_revisions', 'Revisions',
                             DataSetId=data_set):
        identity = revision.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Data Exchange revision is missing its identity')
        found.append(identity)
    return found


def _revisions_per_data_set(asset_type=None):
    """Count revisions per data set, optionally only for one asset type."""
    def check(ctx):
        values = [(identity, len(revisions(identity, ctx)), None)
                  for identity, data_set in data_sets(ctx).items()
                  if asset_type is None or data_set['AssetType'] == asset_type]
        return maximum(values, 'DataSet', 'dataexchange:ListDataSetRevisions')
    return check


def _assets_per_revision(asset_type=None):
    def check(ctx):
        values = []
        for identity, data_set in data_sets(ctx).items():
            if asset_type is not None and data_set['AssetType'] != asset_type:
                continue
            for revision in revisions(identity, ctx):
                assets = ctx.call(DATAEXCHANGE, 'list_revision_assets', 'Assets',
                                  DataSetId=identity, RevisionId=revision)
                values.append((f'{identity}/{revision}', len(assets), None))
        return maximum(values, 'DataSetRevision', 'dataexchange:ListRevisionAssets')
    return check


def running_jobs(ctx):
    """Group the jobs that are still waiting or running by their type."""
    counts = Counter()
    for job in ctx.call(DATAEXCHANGE, 'list_jobs', 'Jobs'):
        state, kind = job.get('State'), job.get('Type')
        if state not in JOB_STATES:
            raise NoData('Data Exchange job has an unknown state')
        if kind not in JOB_TYPES:
            raise NoData('Data Exchange job has an unknown type')
        if state in RUNNING_JOB_STATES:
            counts[kind] += 1
    return counts


def _concurrent_jobs(kind):
    def check(ctx):
        return dict(usage=running_jobs(ctx)[kind], source='dataexchange:ListJobs',
                    method='ACCOUNT_COUNT')
    return check


def data_grants(ctx):
    found = {}
    for grant in ctx.call(DATAEXCHANGE, 'list_data_grants', 'DataGrantSummaries'):
        identity = grant.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Data Exchange data grant is missing its identity')
        found[identity] = grant
    return found


def active_and_pending_data_grants(ctx):
    """Every grant is either accepted or awaiting its receiver, and both count."""
    usage = 0
    for grant in data_grants(ctx).values():
        if grant.get('AcceptanceState') not in GRANT_STATES:
            raise NoData('Data Exchange data grant has an unknown acceptance state')
        usage += 1
    return dict(usage=usage, source='dataexchange:ListDataGrants',
                method='ACCOUNT_COUNT')


def pending_grants_per_consumer(ctx):
    counts = Counter()
    for grant in data_grants(ctx).values():
        if grant.get('AcceptanceState') != 'PENDING_RECEIVER_ACCEPTANCE':
            continue
        consumer = grant.get('ReceiverPrincipal')
        if not isinstance(consumer, str) or not consumer:
            raise NoData('Data Exchange data grant names no receiver')
        counts[consumer] += 1
    return maximum(((consumer, count, None) for consumer, count in counts.items()),
                   'DataGrantReceiver', 'dataexchange:ListDataGrants')


def event_actions_per_data_set(ctx):
    counts = Counter({identity: 0 for identity in data_sets(ctx)})
    for action in ctx.call(DATAEXCHANGE, 'list_event_actions', 'EventActions'):
        event = action.get('Event') or {}
        published = event.get('RevisionPublished') or {}
        source = published.get('DataSetId')
        if not isinstance(source, str) or not source:
            raise NoData('Data Exchange event action names no data set')
        counts[source] += 1
    return maximum(((identity, count, None) for identity, count in counts.items()),
                   'DataSet', 'dataexchange:ListEventActions')


CHECKS = [
    ('L-52E2E63A', 'Data sets per account',
     lambda ctx: dict(usage=len(data_sets(ctx)), source='dataexchange:ListDataSets',
                      method='ACCOUNT_COUNT')),
    ('L-8EB7960E', 'Event actions per account',
     lambda ctx: dict(usage=len(ctx.call(DATAEXCHANGE, 'list_event_actions',
                                         'EventActions')),
                      source='dataexchange:ListEventActions', method='ACCOUNT_COUNT')),
    ('L-375806A0', 'Revisions per data set', _revisions_per_data_set()),
    ('L-70B0F91E', 'Revisions per Amazon S3 data access data set',
     _revisions_per_data_set('S3_DATA_ACCESS')),
    ('L-237CFF3D', 'Revisions per Amazon API Gateway API data set',
     _revisions_per_data_set('API_GATEWAY_API')),
    ('L-A8722A7A', 'Revisions per Amazon Redshift datashare data set',
     _revisions_per_data_set('REDSHIFT_DATA_SHARE')),
    ('L-A15CB065', 'Revisions per AWS Lake Formation data permission data set',
     _revisions_per_data_set('LAKE_FORMATION_DATA_PERMISSION')),
    ('L-92FCD39C', 'Assets per revision', _assets_per_revision()),
    ('L-60973A49', 'Amazon S3 data access assets per revision',
     _assets_per_revision('S3_DATA_ACCESS')),
    ('L-4F329808', 'Amazon API Gateway API assets per revision',
     _assets_per_revision('API_GATEWAY_API')),
    ('L-9961D71E', 'Amazon Redshift datashare assets per revision',
     _assets_per_revision('REDSHIFT_DATA_SHARE')),
    ('L-D470FF0C', 'AWS Lake Formation data permission assets per revision',
     _assets_per_revision('LAKE_FORMATION_DATA_PERMISSION')),
    ('L-307F71B5', 'Concurrent in progress jobs to import assets from Amazon S3',
     _concurrent_jobs('IMPORT_ASSETS_FROM_S3')),
    ('L-50515269', 'Concurrent in progress jobs to import assets from a signed URL',
     _concurrent_jobs('IMPORT_ASSET_FROM_SIGNED_URL')),
    ('L-37C425C6', 'Concurrent in progress jobs to export assets to Amazon S3',
     _concurrent_jobs('EXPORT_ASSETS_TO_S3')),
    ('L-52FCAA8A', 'Concurrent in progress jobs to export assets to a signed URL',
     _concurrent_jobs('EXPORT_ASSET_TO_SIGNED_URL')),
    ('L-09B749AD', 'Concurrent in progress jobs to export revisions to Amazon S3',
     _concurrent_jobs('EXPORT_REVISIONS_TO_S3')),
    ('L-9D7AE86C',
     'Concurrent in progress jobs to import assets from Amazon Redshift datashares',
     _concurrent_jobs('IMPORT_ASSETS_FROM_REDSHIFT_DATA_SHARES')),
    ('L-A1C96D1F',
     'Concurrent in progress jobs to import assets from Amazon API Gateway',
     _concurrent_jobs('IMPORT_ASSET_FROM_API_GATEWAY_API')),
    ('L-7878C4C3', ('Concurrent in progress jobs to create Amazon S3 data access '
                   'assets from S3 buckets'),
     _concurrent_jobs('CREATE_S3_DATA_ACCESS_FROM_S3_BUCKET')),
    ('L-426BE746', ('Concurrent in progress jobs to import assets from an AWS Lake '
                   'Formation tag policy'),
     _concurrent_jobs('IMPORT_ASSETS_FROM_LAKE_FORMATION_TAG_POLICY')),
    ('L-4F23AFE3', 'Active and pending data grants', active_and_pending_data_grants),
    ('L-1FA7039C', 'Pending data grants per consumer', pending_grants_per_consumer),
    ('L-7053BE85', 'Auto export event actions per data set',
     event_actions_per_data_set),
]


def get_current_quotastatus_dataexchange(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dataexchange' for service, _ in context.quotas):
        return []
    return context.run('dataexchange', CHECKS, skip)
