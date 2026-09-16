"""MediaLive and MediaPackage regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env

CUSTOM_KEYS = {('medialive', code) for code in ('L-D1AFAF75', 'L-7BC53EAF',
                                                'L-9E4BC4C0', 'L-A825B11C')} | {
    ('mediapackage', code) for code in ('L-352B8598', 'L-7F7EDDDF')}


def resource(service, method, key):
    return lambda c: dict(usage=len(c.call(service, method, key)),
                          source=f'{service}:{method}', method='ACCOUNT_COUNT')

def max_endpoints_per_channel(ctx):
    values = []
    for channel in ctx.call('mediapackage', 'list_channels', 'Channels'):
        cid = channel.get('id') or channel.get('Id')
        if cid:
            values.append((cid, len(ctx.call('mediapackage', 'list_origin_endpoints', 'OriginEndpoints', ChannelId=cid)), None))
    from modules.qmcore.aws import maximum
    return maximum(values, 'MediaPackageChannel', 'mediapackage:ListOriginEndpoints')


def get_current_quotastatus_streaming(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'medialive' for service, _ in context.quotas):
        entries.extend(context.run('medialive', [
            ('L-D1AFAF75', 'Channels', resource('medialive', 'list_channels', 'Channels')),
            ('L-7BC53EAF', 'Clusters', resource('medialive', 'list_clusters', 'Clusters')),
            ('L-9E4BC4C0', 'CloudWatch Alarm Templates', resource('medialive', 'list_cloud_watch_alarm_templates', 'CloudWatchAlarmTemplates')),
            ('L-A825B11C', 'EventBridge Rule Templates', resource('medialive', 'list_event_bridge_rule_templates', 'EventBridgeRuleTemplates')),
        ], skip))
    if any(service == 'mediapackage' for service, _ in context.quotas):
        entries.extend(context.run('mediapackage', [
            ('L-352B8598', 'Channels', resource('mediapackage', 'list_channels', 'Channels')),
            ('L-7F7EDDDF', 'Endpoints per channel', max_endpoints_per_channel),
        ], skip))
    return entries
