"""Kinesis Video Streams regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('kinesisvideo', method, key)), source=f'kinesisvideo:{method}', method='ACCOUNT_COUNT')


def media_storage_channels(ctx):
    """Count streams configured with media retention.

    Kinesis Video exposes the retention setting in each ``StreamInfo``.  A
    stream with positive ``DataRetentionInHours`` is a media storage channel;
    counting all streams would overstate this quota.
    """
    streams = ctx.call('kinesisvideo', 'list_streams', 'StreamInfoList')
    return dict(usage=sum((stream.get('DataRetentionInHours') or 0) > 0 for stream in streams),
                source='kinesisvideo:ListStreams', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-F06528A6', 'Number of video streams', lambda ctx: count(ctx, 'list_streams', 'StreamInfoList')),
    ('L-B7F419CA', 'Number of signaling channels', lambda ctx: count(ctx, 'list_signaling_channels', 'ChannelInfoList')),
    ('L-B71421B8', 'Number of media storage channels', media_storage_channels),
]


def get_current_quotastatus_kinesisvideo(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kinesisvideo' for service, _ in context.quotas): return []
    return context.run('kinesisvideo', CHECKS, skip)
