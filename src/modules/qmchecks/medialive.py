"""AWS Elemental MediaLive channel, input, cluster and template inventories.

`Pull Inputs` is not measured: MediaLive's input types name the push direction
explicitly but not the pull one, so deciding which of `MP4_FILE`, `TS_FILE`,
`URL_PULL` and the SRT and multicast types the quota counts would be a guess.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

MEDIALIVE = 'medialive'
INPUT_TYPES = {'UDP_PUSH', 'RTP_PUSH', 'RTMP_PUSH', 'RTMP_PULL', 'URL_PULL',
               'MP4_FILE', 'MEDIACONNECT', 'INPUT_DEVICE', 'AWS_CDI', 'TS_FILE',
               'SRT_CALLER', 'MULTICAST', 'SMPTE_2110_RECEIVER_GROUP', 'SDI',
               'MEDIACONNECT_ROUTER', 'SRT_LISTENER'}
PUSH_TYPES = {'UDP_PUSH', 'RTP_PUSH', 'RTMP_PUSH'}
MEDIACONNECT_TYPES = {'MEDIACONNECT', 'MEDIACONNECT_ROUTER'}
NETWORK_LOCATIONS = {'AWS', 'ON_PREMISES'}
CODECS = {'MPEG2', 'AVC', 'HEVC'}
RESOLUTIONS = {'SD', 'HD', 'UHD'}


def _count(method, key, source):
    return lambda ctx: dict(usage=len(ctx.call(MEDIALIVE, method, key)),
                            source=source, method='ACCOUNT_COUNT')


def inputs(ctx):
    found = {}
    for entry in ctx.call(MEDIALIVE, 'list_inputs', 'Inputs'):
        identity = entry.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('MediaLive input is missing its identity')
        if entry.get('Type') not in INPUT_TYPES:
            raise NoData('MediaLive input has an unknown type')
        found[identity] = entry
    return found


def _inputs_of_type(types):
    def check(ctx):
        usage = sum(entry['Type'] in types for entry in inputs(ctx).values())
        return dict(usage=usage, source='medialive:ListInputs',
                    method='ACCOUNT_COUNT')
    return check


def anywhere_inputs(ctx):
    """An input placed on premises belongs to MediaLive Anywhere."""
    usage = 0
    for entry in inputs(ctx).values():
        location = entry.get('InputNetworkLocation')
        if location is None:
            continue
        if location not in NETWORK_LOCATIONS:
            raise NoData('MediaLive input has an unknown network location')
        usage += location == 'ON_PREMISES'
    return dict(usage=usage, source='medialive:ListInputs', method='ACCOUNT_COUNT')


def vpc_inputs(ctx):
    usage = sum(bool(entry.get('Destinations') and any(
        destination.get('Vpc') for destination in entry['Destinations']))
        for entry in inputs(ctx).values())
    return dict(usage=usage, source='medialive:ListInputs', method='ACCOUNT_COUNT')


def channels(ctx):
    found = {}
    for channel in ctx.call(MEDIALIVE, 'list_channels', 'Channels'):
        identity = channel.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('MediaLive channel is missing its identity')
        found[identity] = channel
    return found


def _channels_by_specification(field, allowed, wanted):
    """Read the codec or resolution each channel's input specification names."""
    def check(ctx):
        usage = 0
        for channel in channels(ctx).values():
            specification = channel.get('InputSpecification') or {}
            value = specification.get(field)
            if value is None:
                continue
            if value not in allowed:
                raise NoData(f'MediaLive channel has an unknown {field.lower()}')
            usage += value == wanted
        return dict(usage=usage, source='medialive:ListChannels',
                    method='ACCOUNT_COUNT')
    return check


def cdi_channels(ctx):
    usage = sum(bool(channel.get('CdiInputSpecification'))
                for channel in channels(ctx).values())
    return dict(usage=usage, source='medialive:ListChannels',
                method='ACCOUNT_COUNT')


def clusters(ctx):
    found = []
    for cluster in ctx.call(MEDIALIVE, 'list_clusters', 'Clusters'):
        identity = cluster.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('MediaLive cluster is missing its identity')
        found.append(identity)
    return found


def _per_cluster(method, key, source):
    def check(ctx):
        values = [(identity, len(ctx.call(MEDIALIVE, method, key,
                                          ClusterId=identity)), None)
                  for identity in clusters(ctx)]
        return maximum(values, 'MediaLiveCluster', source)
    return check


CHECKS = [
    ('L-9E233AF7', 'Push Inputs', _inputs_of_type(PUSH_TYPES)),
    ('L-BDF24E14', 'Device Inputs', _inputs_of_type({'INPUT_DEVICE'})),
    ('L-FBCE2FC3', 'MediaConnect Inputs', _inputs_of_type(MEDIACONNECT_TYPES)),
    ('L-68E02936', 'VPC Inputs', vpc_inputs),
    ('L-A4814CCC', 'Anywhere Inputs', anywhere_inputs),
    ('L-6A0116BB', 'Input Security Groups',
     _count('list_input_security_groups', 'InputSecurityGroups',
            'medialive:ListInputSecurityGroups')),
    ('L-3FDA265B', 'CDI Channels', cdi_channels),
    ('L-05A796F2', 'HEVC Channels',
     _channels_by_specification('Codec', CODECS, 'HEVC')),
    ('L-DDE858F0', 'UHD Channels',
     _channels_by_specification('Resolution', RESOLUTIONS, 'UHD')),
    ('L-8B49C5C1', 'Multiplexes',
     _count('list_multiplexes', 'Multiplexes', 'medialive:ListMultiplexes')),
    ('L-3C46E17E', 'Networks',
     _count('list_networks', 'Networks', 'medialive:ListNetworks')),
    ('L-1F6E2FAF', 'Reservations',
     _count('list_reservations', 'Reservations', 'medialive:ListReservations')),
    ('L-AAFBD428', 'SDI sources',
     _count('list_sdi_sources', 'SdiSources', 'medialive:ListSdiSources')),
    ('L-B0CA93DC', 'Signal Maps',
     _count('list_signal_maps', 'SignalMaps', 'medialive:ListSignalMaps')),
    ('L-759E3395', 'CloudWatch Alarm Template Groups',
     _count('list_cloud_watch_alarm_template_groups',
            'CloudWatchAlarmTemplateGroups',
            'medialive:ListCloudWatchAlarmTemplateGroups')),
    ('L-9E4BC4C0', 'CloudWatch Alarm Templates',
     _count('list_cloud_watch_alarm_templates', 'CloudWatchAlarmTemplates',
            'medialive:ListCloudWatchAlarmTemplates')),
    ('L-019F695A', 'EventBridge Rule Template Groups',
     _count('list_event_bridge_rule_template_groups',
            'EventBridgeRuleTemplateGroups',
            'medialive:ListEventBridgeRuleTemplateGroups')),
    ('L-A825B11C', 'EventBridge Rule Templates',
     _count('list_event_bridge_rule_templates', 'EventBridgeRuleTemplates',
            'medialive:ListEventBridgeRuleTemplates')),
    ('L-22ED1BEF', 'Nodes per Cluster',
     _per_cluster('list_nodes', 'Nodes', 'medialive:ListNodes')),
    ('L-FF7E5CAC', 'Channel Placement Groups per Cluster',
     _per_cluster('list_channel_placement_groups', 'ChannelPlacementGroups',
                  'medialive:ListChannelPlacementGroups')),
]


def get_current_quotastatus_medialive(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'medialive' for service, _ in context.quotas):
        return []
    return context.run('medialive', CHECKS, skip)
