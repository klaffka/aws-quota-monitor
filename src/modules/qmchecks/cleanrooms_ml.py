"""Clean Rooms ML resource checks scoped to the creator's memberships."""
from collections import defaultdict
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env
from modules.qmchecks.cleanrooms_ml_quotas import TRAINING_INSTANCE_QUOTAS

PENDING = {'CREATE_PENDING', 'CREATE_IN_PROGRESS'}
FINISHED = {'CREATE_FAILED', 'ACTIVE', 'INACTIVE'}
DELETING = {'DELETE_PENDING', 'DELETE_IN_PROGRESS', 'DELETE_FAILED'}
CANCELLING = {'CANCEL_PENDING', 'CANCEL_IN_PROGRESS', 'CANCEL_FAILED'}


def identity(item, key):
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise NoData(f'Clean Rooms ML inventory is missing {key}')
    return value


def memberships(ctx):
    # ListMemberships returns memberships owned by this account. Collaborations
    # can also expose other members' models; those are not this inventory.
    found = set()
    for member in ctx.call('cleanrooms', 'list_memberships', 'membershipSummaries'):
        mid = identity(member, 'id')
        if mid not in found:
            found.add(mid)
            yield mid


def unique(items, key, membership=None):
    found = {}
    for item in items:
        rid = tuple(identity(item, field) for field in key) if isinstance(key, tuple) else identity(item, key)
        if membership is not None and item.get('membershipIdentifier') != membership:
            raise NoData('Clean Rooms ML inventory has a different creator membership')
        if rid in found and found[rid] != item:
            raise NoData('Clean Rooms ML resource changed during pagination')
        found[rid] = item
    return list(found.values())


def model_versions(ctx):
    for mid in memberships(ctx):
        roots = unique(ctx.call('cleanroomsml', 'list_trained_models', 'trainedModels',
                                membershipIdentifier=mid), 'trainedModelArn', mid)
        for root in roots:
            arn = root['trainedModelArn']
            items = ctx.call('cleanroomsml', 'list_trained_model_versions', 'trainedModels',
                             membershipIdentifier=mid, trainedModelArn=arn)
            if not items:
                raise NoData('Clean Rooms ML model exists but version inventory is empty')
            found = {}
            for item in items:
                if item.get('membershipIdentifier') != mid or item.get('trainedModelArn') != arn:
                    raise NoData('Clean Rooms ML model version has a different identity')
                version = item.get('versionIdentifier')
                # Legacy base models may have no version ID. They can be read
                # without a version parameter only when the root has no ID too.
                if version is None and root.get('versionIdentifier') is not None:
                    raise NoData('Clean Rooms ML version identity is missing')
                if version is not None and (not isinstance(version, str) or not version):
                    raise NoData('Clean Rooms ML version identity is invalid')
                if version in found and found[version] != item:
                    raise NoData('Clean Rooms ML model version changed during pagination')
                found[version] = item
            if root.get('versionIdentifier') not in found:
                raise NoData('Clean Rooms ML version inventory omitted the listed model version')
            for version, item in found.items():
                yield mid, arn, version, item


def pending_count(items, allow_deleting=True):
    count = 0
    for item in items:
        state = item.get('status')
        if state in PENDING:
            count += 1
        elif state not in FINISHED | (DELETING if allow_deleting else set()):
            raise NoData('Clean Rooms ML job has unknown or cancelling quota reservation')
    return count


def training_jobs(ctx, per_membership=False):
    grouped = defaultdict(list)
    for mid, _, _, item in model_versions(ctx):
        grouped[mid].append(item)
    values = [(mid, pending_count(items), None) for mid, items in grouped.items()]
    if per_membership:
        return maximum(values, 'CleanRoomsMembership', 'cleanrooms-ml:ListTrainedModelVersions')
    return dict(usage=sum(value[1] for value in values), source='cleanrooms-ml:ListTrainedModelVersions', method='ACCOUNT_COUNT')


def active_versions(ctx):
    counts = defaultdict(int)
    for _mid, arn, _, item in model_versions(ctx):
        state = item.get('status')
        if state in PENDING | {'ACTIVE'}:
            counts[arn] += 1
        elif state not in {'CREATE_FAILED', 'INACTIVE'} | DELETING:
            raise NoData('Clean Rooms ML model version has an unknown quota state')
    return maximum([(arn, count, None) for arn, count in counts.items()],
                   'TrainedModel', 'cleanrooms-ml:ListTrainedModelVersions')


def training_instances(ctx, instance_type=None):
    count = 0
    for mid, arn, version, item in model_versions(ctx):
        state = item.get('status')
        if state in FINISHED:
            continue  # ACTIVE denotes a trained model artifact, not a running job.
        if state not in PENDING | DELETING | CANCELLING:
            raise NoData('Clean Rooms ML model has an unknown training state')
        params = dict(membershipIdentifier=mid, trainedModelArn=arn)
        if version is not None:
            params['versionIdentifier'] = version
        detail = ctx.call('cleanroomsml', 'get_trained_model', **params)
        if (detail.get('membershipIdentifier') != mid or detail.get('trainedModelArn') != arn
                or detail.get('versionIdentifier') != version or detail.get('status') != state):
            raise NoData('Clean Rooms ML training model changed or returned a different version')
        config = detail.get('resourceConfig') or {}
        kind = config.get('instanceType')
        if not isinstance(kind, str) or not kind:
            raise NoData('Clean Rooms ML training model has no instance type')
        if instance_type is not None and kind != instance_type:
            continue
        if state != 'CREATE_IN_PROGRESS':
            raise NoData(f'Clean Rooms ML instance reservation is unverified in state {state}')
        amount = config.get('instanceCount')
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 1:
            raise NoData('Clean Rooms ML training model has no valid instance count')
        count += amount
    return dict(usage=count, source='cleanrooms-ml:ListTrainedModelVersions+GetTrainedModel',
                method='ACCOUNT_COUNT', meta={'instanceType': instance_type})


def inference_jobs(ctx, per_membership=False):
    values = []
    for mid in memberships(ctx):
        items = unique(ctx.call('cleanroomsml', 'list_trained_model_inference_jobs', 'trainedModelInferenceJobs',
                                membershipIdentifier=mid), 'trainedModelInferenceJobArn', mid)
        values.append((mid, pending_count(items, allow_deleting=False), None))
    if per_membership:
        return maximum(values, 'CleanRoomsMembership', 'cleanrooms-ml:ListTrainedModelInferenceJobs')
    return dict(usage=sum(value[1] for value in values), source='cleanrooms-ml:ListTrainedModelInferenceJobs', method='ACCOUNT_COUNT')


def membership_inventory(ctx, method, key, id_key, active=False):
    values = []
    for mid in memberships(ctx):
        items = unique(ctx.call('cleanroomsml', method, key, membershipIdentifier=mid), id_key, mid)
        if active:
            if any(item.get('status') not in PENDING | FINISHED | DELETING for item in items):
                raise NoData('Clean Rooms ML input channel has an unknown status')
            items = [item for item in items if item['status'] == 'ACTIVE']
        values.append((mid, len(items), None))
    return maximum(values, 'CleanRoomsMembership', f'cleanrooms-ml:{method}')


def audience_jobs(ctx, method, key, id_key):
    items = unique(ctx.call('cleanroomsml', method, key), id_key)
    return dict(usage=pending_count(items), source=f'cleanrooms-ml:{method}', method='ACCOUNT_COUNT')


CHECKS = [(code, f'{kind} training instances per account', partial(training_instances, instance_type=kind))
          for code, kind in TRAINING_INSTANCE_QUOTAS]
CHECKS += [
    ('L-FF7AD06D', 'Active training instances per account', training_instances),
    ('L-007D6EC0', 'Pending/in-progress training jobs per account', training_jobs),
    ('L-F6FC5155', 'Pending/in-progress training jobs per membership', partial(training_jobs, per_membership=True)),
    ('L-BE951A3C', 'Active/pending/in-progress versions per trained model', active_versions),
    ('L-249F4B83', 'Pending/in-progress inference jobs per account', inference_jobs),
    ('L-0F77DDDB', 'Pending/in-progress inference jobs per membership', partial(inference_jobs, per_membership=True)),
    ('L-F2D3388D', 'Active input channels per membership', partial(membership_inventory,
        method='list_ml_input_channels', key='mlInputChannelsList', id_key='mlInputChannelArn', active=True)),
    ('L-98291B04', 'Configured model algorithm associations per membership', partial(membership_inventory,
        method='list_configured_model_algorithm_associations', key='configuredModelAlgorithmAssociations',
        id_key='configuredModelAlgorithmAssociationArn')),
    ('L-11056252', 'Pending/in-progress audience models', partial(audience_jobs,
        method='list_audience_models', key='audienceModels', id_key='audienceModelArn')),
    ('L-2396565D', 'Pending/in-progress audience generation jobs', partial(audience_jobs,
        method='list_audience_generation_jobs', key='audienceGenerationJobs', id_key='audienceGenerationJobArn')),
    ('L-907EBCEA', 'Pending/in-progress audience export jobs', partial(audience_jobs,
        method='list_audience_export_jobs', key='audienceExportJobs', id_key=('audienceGenerationJobArn', 'name'))),
]


def get_current_quotastatus_cleanrooms_ml(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    selected = [check for check in CHECKS if ('cleanrooms-ml', check[0]) in context.quotas]
    return context.run('cleanrooms-ml', selected, skip) if selected else []
