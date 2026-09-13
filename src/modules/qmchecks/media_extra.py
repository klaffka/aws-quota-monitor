"""Additional MediaConnect and MediaPackage V2 resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

CUSTOM_KEYS = {('mediaconnect', code) for code in ('L-F1F62F5D', 'L-A99016A8', 'L-075679EF')} | {
    ('mediapackagev2', code) for code in ('L-A7040149', 'L-55777135', 'L-305BEE26')}


def count(service, method, key):
    return lambda c: dict(usage=len(c.call(service, method, key)),
                          source=f'{service}:{method}', method='ACCOUNT_COUNT')


def max_channels_per_group(c):
    values = []
    for group in c.call('mediapackagev2', 'list_channel_groups', 'ChannelGroups'):
        name = group.get('ChannelGroupName')
        values.append((name, len(c.call('mediapackagev2', 'list_channels', 'Items', ChannelGroupName=name)), None))
    return maximum(values, 'ChannelGroup', 'mediapackagev2:ListChannels')


def max_endpoints_per_channel(c):
    values = []
    for group in c.call('mediapackagev2', 'list_channel_groups', 'ChannelGroups'):
        group_name = group.get('ChannelGroupName')
        for channel in c.call('mediapackagev2', 'list_channels', 'Items', ChannelGroupName=group_name):
            name = channel.get('ChannelName')
            values.append((name, len(c.call('mediapackagev2', 'list_origin_endpoints', 'Items',
                                             ChannelGroupName=group_name, ChannelName=name)), None))
    return maximum(values, 'Channel', 'mediapackagev2:ListOriginEndpoints')


def get_current_quotastatus_media_extra(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'mediaconnect' for service, _ in context.quotas):
        entries.extend(context.run('mediaconnect', [
            ('L-F1F62F5D', 'Entitlements', count('mediaconnect', 'list_entitlements', 'Entitlements')),
            ('L-A99016A8', 'Flows', count('mediaconnect', 'list_flows', 'Flows')),
            ('L-075679EF', 'Bridges', count('mediaconnect', 'list_bridges', 'Bridges')),
        ], skip))
    if any(service == 'mediapackagev2' for service, _ in context.quotas):
        entries.extend(context.run('mediapackagev2', [
            ('L-A7040149', 'Channel Groups', count('mediapackagev2', 'list_channel_groups', 'ChannelGroups')),
            ('L-55777135', 'Channels per channel group', max_channels_per_group),
            ('L-305BEE26', 'Origin endpoints per channel', max_endpoints_per_channel),
        ], skip))
    return entries
