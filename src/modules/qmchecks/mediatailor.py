"""AWS Elemental MediaTailor regional resource inventories.

`Live Sources`, `VOD Sources` and `Package configurations` name no scope, and
their listings are scoped to a source location, so neither an account total nor
a per-location maximum can be shown to be the quota AWS applies. They stay in
the audit rather than being measured against a denominator picked by guess.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

MEDIATAILOR = 'mediatailor'


def count(ctx, method, key):
    return dict(usage=len(ctx.call(MEDIATAILOR, method, key)),
                source=f'mediatailor:{method}', method='ACCOUNT_COUNT')


def outputs_per_channel(ctx):
    """ListChannels already carries each channel's outputs."""
    values = []
    for channel in ctx.call(MEDIATAILOR, 'list_channels', 'Items'):
        name = channel.get('ChannelName')
        if not isinstance(name, str) or not name:
            raise NoData('MediaTailor channel is missing its name')
        values.append((name, len(channel.get('Outputs') or ()), None))
    return maximum(values, 'MediaTailorChannel', 'mediatailor:ListChannels')


def segment_delivery_per_source_location(ctx):
    values = []
    for location in ctx.call(MEDIATAILOR, 'list_source_locations', 'Items'):
        name = location.get('SourceLocationName')
        if not isinstance(name, str) or not name:
            raise NoData('MediaTailor source location is missing its name')
        detail = ctx.call(MEDIATAILOR, 'describe_source_location', SourceLocationName=name)
        if detail.get('SourceLocationName') != name:
            raise NoData('MediaTailor source location detail has a different identity')
        values.append((name, len(detail.get('SegmentDeliveryConfigurations') or ()), None))
    return maximum(values, 'MediaTailorSourceLocation',
                   'mediatailor:ListSourceLocations+DescribeSourceLocation')


CHECKS = [
    ('L-2290981E', 'Source Locations', lambda ctx: count(ctx, 'list_source_locations', 'Items')),
    ('L-29DF1B92', 'Channels per account', lambda ctx: count(ctx, 'list_channels', 'Items')),
    ('L-F60EC97B', 'Configurations',
     lambda ctx: count(ctx, 'list_playback_configurations', 'Items')),
    ('L-3BCD6A29', 'Channel outputs', outputs_per_channel),
    ('L-680CE323', 'Segment Delivery Configurations Per Source',
     segment_delivery_per_source_location),
]


def get_current_quotastatus_mediatailor(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediatailor' for service, _ in context.quotas): return []
    return context.run('mediatailor', CHECKS, skip)
