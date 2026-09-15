"""Amazon Chime SDK identity, messaging, voice and media pipeline quotas.

Meeting quotas (attendees, concurrent meetings, video streams, replicas) have no
inventory API: a meeting exists only while it runs and cannot be listed. Active
call limits and concurrent connections per app instance user are in-flight
counts for the same reason, and the message prefetch quotas bound the contents
of a single event.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

IDENTITY = 'chime-sdk-identity'
MESSAGING = 'chime-sdk-messaging'
VOICE = 'chime-sdk-voice'
PIPELINES = 'chime-sdk-media-pipelines'


def _arn(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Chime SDK {subject} is missing its ARN')
    return value


def app_instances(ctx):
    found = []
    for item in ctx.call(IDENTITY, 'list_app_instances', 'AppInstances'):
        arn = _arn(item, 'AppInstanceArn', 'app instance')
        if arn not in found:
            found.append(arn)
    return found


def app_instance_users(app_instance, ctx):
    return [_arn(item, 'AppInstanceUserArn', 'app instance user')
            for item in ctx.call(IDENTITY, 'list_app_instance_users',
                                 'AppInstanceUsers', AppInstanceArn=app_instance)]


def _per_app_instance(method, key, service=IDENTITY, source=None):
    def check(ctx):
        values = [(arn, len(ctx.call(service, method, key, AppInstanceArn=arn)), None)
                  for arn in app_instances(ctx)]
        return maximum(values, 'ChimeAppInstance', source)
    return check


def users_per_app_instance(ctx):
    values = [(arn, len(app_instance_users(arn, ctx)), None)
              for arn in app_instances(ctx)]
    return maximum(values, 'ChimeAppInstance',
                   'chime-sdk-identity:ListAppInstanceUsers')


def endpoints_per_user(ctx):
    values = []
    for app_instance in app_instances(ctx):
        for user in app_instance_users(app_instance, ctx):
            endpoints = ctx.call(IDENTITY, 'list_app_instance_user_endpoints',
                                 'AppInstanceUserEndpoints', AppInstanceUserArn=user)
            values.append((user, len(endpoints), None))
    return maximum(values, 'ChimeAppInstanceUser',
                   'chime-sdk-identity:ListAppInstanceUserEndpoints')


def processors_per_channel_flow(ctx):
    """Channel flow summaries already carry their processor list."""
    values = []
    for app_instance in app_instances(ctx):
        for flow in ctx.call(MESSAGING, 'list_channel_flows', 'ChannelFlows',
                             AppInstanceArn=app_instance):
            arn = _arn(flow, 'ChannelFlowArn', 'channel flow')
            processors = flow.get('Processors')
            if not isinstance(processors, list):
                raise NoData('Chime SDK channel flow has no processors')
            values.append((arn, len(processors), None))
    return maximum(values, 'ChimeChannelFlow',
                   'chime-sdk-messaging:ListChannelFlows')


def applications_per_sip_rule(ctx):
    values = []
    for rule in ctx.call(VOICE, 'list_sip_rules', 'SipRules'):
        identity = rule.get('SipRuleId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Chime SDK SIP rule is missing its identity')
        targets = rule.get('TargetApplications')
        if not isinstance(targets, list):
            raise NoData('Chime SDK SIP rule has no target applications')
        values.append((identity, len(targets), None))
    return maximum(values, 'ChimeSipRule', 'chime-sdk-voice:ListSipRules')


def media_pipelines(ctx):
    found = []
    for item in ctx.call(PIPELINES, 'list_media_pipelines', 'MediaPipelines'):
        identity = item.get('MediaPipelineId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Chime SDK media pipeline is missing its identity')
        if identity not in found:
            found.append(identity)
    return found


def call_analytics_pipelines(ctx):
    """Only a media insights pipeline counts towards the call analytics quota."""
    usage = 0
    for identity in media_pipelines(ctx):
        pipeline = ctx.call(PIPELINES, 'get_media_pipeline',
                            MediaPipelineId=identity).get('MediaPipeline')
        if not isinstance(pipeline, dict) or not pipeline:
            raise NoData('Chime SDK media pipeline has no detail')
        usage += 'MediaInsightsPipeline' in pipeline
    return dict(usage=usage, source='chime-sdk-media-pipelines:GetMediaPipeline',
                method='ACCOUNT_COUNT')


def _account_count(service, method, key, source):
    return lambda ctx: dict(usage=len(ctx.call(service, method, key)),
                            source=source, method='ACCOUNT_COUNT')


CHECKS = [
    ('L-0222B40A', 'Amazon Chime SDK Identity - Maximum AppInstances per AWS Account',
     lambda ctx: dict(usage=len(app_instances(ctx)),
                      source='chime-sdk-identity:ListAppInstances',
                      method='ACCOUNT_COUNT')),
    ('L-D54E9933', 'Amazon Chime SDK Identity - Maximum AppInstanceUsers per AppInstance',
     users_per_app_instance),
    ('L-9A7ECB60', 'Amazon Chime SDK Identity - Maximum AppInstanceUserAdmins per AppInstance',
     _per_app_instance('list_app_instance_admins', 'AppInstanceAdmins',
                       source='chime-sdk-identity:ListAppInstanceAdmins')),
    ('L-39BCA56C',
     'Amazon Chime SDK Identity - Maximum AppInstanceUserEndpoints per AppInstanceUser',
     endpoints_per_user),
    ('L-D1550AB5', 'Amazon Chime SDK Messaging - Maximum ChannelFlows per AppInstance',
     _per_app_instance('list_channel_flows', 'ChannelFlows', service=MESSAGING,
                       source='chime-sdk-messaging:ListChannelFlows')),
    ('L-CA0C986A', 'Amazon Chime SDK Messaging - Maximum ChannelProcessors per ChannelFlow',
     processors_per_channel_flow),
    ('L-8EE806B4', 'Amazon Chime SDK SIP trunking and voice - Voice Connectors',
     _account_count(VOICE, 'list_voice_connectors', 'VoiceConnectors',
                    'chime-sdk-voice:ListVoiceConnectors')),
    ('L-9DD490AB',
     'Amazon Chime SDK SIP trunking and voice - SIP media applications',
     _account_count(VOICE, 'list_sip_media_applications', 'SipMediaApplications',
                    'chime-sdk-voice:ListSipMediaApplications')),
    ('L-8BA4EAA6',
     'Amazon Chime SDK SIP trunking and voice - SIP media applications per SIP rule',
     applications_per_sip_rule),
    ('L-7F583998', 'Amazon Chime SDK media pipeline - Maximum pipelines',
     lambda ctx: dict(usage=len(media_pipelines(ctx)),
                      source='chime-sdk-media-pipelines:ListMediaPipelines',
                      method='ACCOUNT_COUNT')),
    ('L-83E6B280',
     'Amazon Chime SDK media pipeline - Maximum Amazon Kinesis Video Stream pools',
     _account_count(PIPELINES, 'list_media_pipeline_kinesis_video_stream_pools',
                    'KinesisVideoStreamPools',
                    'chime-sdk-media-pipelines:ListMediaPipelineKinesisVideoStreamPools')),
    ('L-668D1758', 'Amazon Chime SDK call analytics - Maximum configurations',
     _account_count(PIPELINES, 'list_media_insights_pipeline_configurations',
                    'MediaInsightsPipelineConfigurations',
                    'chime-sdk-media-pipelines:ListMediaInsightsPipelineConfigurations')),
    ('L-DA073F3A', 'Amazon Chime SDK call analytics - Maximum pipelines',
     call_analytics_pipelines),
]


def get_current_quotastatus_chime(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'chime' for service, _ in context.quotas):
        return []
    return context.run('chime', CHECKS, skip)
