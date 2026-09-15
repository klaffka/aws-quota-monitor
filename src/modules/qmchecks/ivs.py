"""Amazon Interactive Video Service resource inventories.

Compositions and stage participants are live resources: a composition that has
stopped no longer occupies the quota, and only a connected participant does.
"""
from collections import defaultdict

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

IVS = 'ivs'
REALTIME = 'ivs-realtime'
COMPOSITION_STATES = {'STARTING', 'ACTIVE', 'STOPPING', 'FAILED', 'STOPPED'}
LIVE_COMPOSITION_STATES = {'STARTING', 'ACTIVE', 'STOPPING'}
PARTICIPANT_STATES = {'CONNECTED', 'DISCONNECTED'}


def _count(service, method, key):
    source = service + ':' + ''.join(part.capitalize() for part in method.split('_'))
    return lambda ctx: dict(usage=len(ctx.call(service, method, key)), source=source,
                            method='ACCOUNT_COUNT')


def compositions(ctx):
    """Return the compositions that still hold capacity, by stage."""
    found = defaultdict(list)
    for composition in ctx.call(REALTIME, 'list_compositions', 'compositions'):
        state = composition.get('state')
        if state not in COMPOSITION_STATES:
            raise NoData('IVS composition has an unknown state')
        stage = composition.get('stageArn')
        if not isinstance(stage, str) or not stage:
            raise NoData('IVS composition is missing its stage')
        if state in LIVE_COMPOSITION_STATES:
            found[stage].append(composition)
    return found


def live_compositions(ctx):
    usage = sum(len(entries) for entries in compositions(ctx).values())
    return dict(usage=usage, source='ivs-realtime:ListCompositions',
                method='ACCOUNT_COUNT')


def compositions_per_stage(ctx):
    return maximum(((stage, len(entries), None)
                    for stage, entries in compositions(ctx).items()),
                   'IVSStage', 'ivs-realtime:ListCompositions')


def destinations_per_composition(ctx):
    values = []
    for entries in compositions(ctx).values():
        for composition in entries:
            destinations = composition.get('destinations')
            if not isinstance(destinations, list):
                raise NoData('IVS composition is missing its destination list')
            values.append((composition['arn'], len(destinations), None))
    return maximum(values, 'IVSComposition', 'ivs-realtime:ListCompositions')


def stream_keys_per_channel(ctx):
    values = []
    for channel in ctx.call(IVS, 'list_channels', 'channels'):
        arn = channel.get('arn')
        if not isinstance(arn, str) or not arn:
            raise NoData('IVS channel is missing its ARN')
        keys = ctx.call(IVS, 'list_stream_keys', 'streamKeys', channelArn=arn)
        values.append((arn, len(keys), None))
    return maximum(values, 'IVSChannel', 'ivs:ListChannels+ListStreamKeys')


def publishers_per_stage(ctx):
    """Count the connected publishers of each stage's active session."""
    values = []
    for stage in ctx.call(REALTIME, 'list_stages', 'stages'):
        arn, session = stage.get('arn'), stage.get('activeSessionId')
        if not isinstance(arn, str) or not arn:
            raise NoData('IVS stage is missing its ARN')
        if not session:
            # A stage without an active session has no participants at all.
            values.append((arn, 0, None))
            continue
        usage = 0
        for participant in ctx.call(REALTIME, 'list_participants', 'participants',
                                    stageArn=arn, sessionId=session,
                                    filterByPublished=True):
            state = participant.get('state')
            if state is not None and state not in PARTICIPANT_STATES:
                raise NoData('IVS participant has an unknown state')
            usage += state != 'DISCONNECTED'
        values.append((arn, usage, None))
    return maximum(values, 'IVSStage', 'ivs-realtime:ListStages+ListParticipants')


CHECKS = [
    ('L-C01DFF58', 'Channels', _count(IVS, 'list_channels', 'channels')),
    ('L-90ABAB37', 'Recording configurations',
     _count(IVS, 'list_recording_configurations', 'recordingConfigurations')),
    ('L-BF843A02', 'Storage configurations',
     _count(REALTIME, 'list_storage_configurations', 'storageConfigurations')),
    ('L-F7C5B6C9', 'Encoder configurations',
     _count(REALTIME, 'list_encoder_configurations', 'encoderConfigurations')),
    ('L-CE6ADDBE', 'Ingest configurations',
     _count(REALTIME, 'list_ingest_configurations', 'ingestConfigurations')),
    ('L-47F0B706', 'Stages', _count(REALTIME, 'list_stages', 'stages')),
    ('L-DA157FF6', 'Public keys', _count(REALTIME, 'list_public_keys', 'publicKeys')),
    ('L-5339BD50', 'Playback authorization key pairs',
     _count(IVS, 'list_playback_key_pairs', 'keyPairs')),
    ('L-BF6EB49C', 'Playback restriction policies',
     _count(IVS, 'list_playback_restriction_policies', 'playbackRestrictionPolicies')),
    ('L-D15E1F21', 'Ad configurations',
     _count(IVS, 'list_ad_configurations', 'adConfigurations')),
    ('L-E945C199', 'Compositions', live_compositions),
    ('L-21B2923F', 'Concurrent Compositions per Stage', compositions_per_stage),
    ('L-9C6AF7E0', 'Total number of Destinations per Composition',
     destinations_per_composition),
    ('L-80F95143', 'Stream Key', stream_keys_per_channel),
    ('L-9965E8BE', 'Stage participants (publishers)', publishers_per_stage),
]


def get_current_quotastatus_ivs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ivs' for service, _ in context.quotas):
        return []
    return context.run('ivs', CHECKS, skip)
