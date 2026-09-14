"""Additional MediaConnect and MediaPackage V2 resource inventories."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CUSTOM_KEYS = {('mediaconnect', code) for code in (
    'L-F1F62F5D', 'L-A99016A8', 'L-075679EF', 'L-CB77E87E',
    'L-77138741', 'L-58DF4801', 'L-6C50CD26')} | {
    ('mediapackagev2', code) for code in ('L-A7040149', 'L-55777135', 'L-305BEE26')}

FLOW_STATES = {'STANDBY', 'ACTIVE', 'UPDATING', 'DELETING', 'STARTING', 'STOPPING', 'ERROR'}
ROUTER_IO_STATES = {
    'CREATING', 'STANDBY', 'STARTING', 'ACTIVE', 'STOPPING', 'DELETING',
    'UPDATING', 'ERROR', 'RECOVERING', 'MIGRATING',
}
ROUTER_INTERFACE_STATES = {'CREATING', 'ACTIVE', 'UPDATING', 'DELETING', 'ERROR', 'RECOVERING'}


def count(service, method, key):
    return lambda c: dict(usage=len(c.call(service, method, key)),
                          source=f'{service}:{method}', method='ACCOUNT_COUNT')


def _unique(items, identity_field, arn_field, subject):
    result = {}
    arns = set()
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'MediaConnect {subject} inventory contains an invalid item')
        identity = item.get(identity_field)
        arn = item.get(arn_field)
        if (not isinstance(identity, str) or not identity
                or not isinstance(arn, str) or not arn):
            raise NoData(f'MediaConnect {subject} is missing required identity data')
        if identity in result:
            if result[identity] != item:
                raise NoData(f'MediaConnect {subject} changed during pagination')
            continue
        if arn in arns:
            raise NoData(f'MediaConnect {subject} inventory contains a duplicate ARN')
        result[identity] = item
        arns.add(arn)
    return result.values()


def outputs_per_flow(ctx):
    values = []
    flows = _unique(ctx.call('mediaconnect', 'list_flows', 'Flows'),
                    'FlowArn', 'FlowArn', 'flow')
    for summary in flows:
        arn = summary['FlowArn']
        if summary.get('Status') not in FLOW_STATES:
            raise NoData('MediaConnect flow has an unknown state')
        response = ctx.call('mediaconnect', 'describe_flow', FlowArn=arn)
        flow = response.get('Flow') if isinstance(response, dict) else None
        if (not isinstance(flow, dict) or flow.get('FlowArn') != arn
                or flow.get('Status') != summary['Status']):
            raise NoData('MediaConnect flow detail is missing or inconsistent')
        outputs = flow.get('Outputs')
        if not isinstance(outputs, list):
            raise NoData('MediaConnect flow has no complete output inventory')
        unique_outputs = _unique(outputs, 'OutputArn', 'OutputArn', 'flow output')
        values.append((arn, len(list(unique_outputs)), None))
    return maximum(values, 'MediaConnectFlow',
                   'mediaconnect:ListFlows+DescribeFlow')


def router_count(ctx, method, key, states):
    items = _unique(ctx.call('mediaconnect', method, key), 'Id', 'Arn', key)
    count_in_region = 0
    for item in items:
        region = item.get('RegionName')
        if not isinstance(region, str) or not region:
            raise NoData(f'MediaConnect {key} is missing its Region')
        if item.get('State') not in states:
            raise NoData(f'MediaConnect {key} has an unknown state')
        count_in_region += region == ctx.region
    return dict(usage=count_in_region, source=f'mediaconnect:{method}',
                method='ACCOUNT_COUNT')


MEDIACONNECT_CHECKS = [
    ('L-F1F62F5D', 'Entitlements', count('mediaconnect', 'list_entitlements', 'Entitlements')),
    ('L-A99016A8', 'Flows', count('mediaconnect', 'list_flows', 'Flows')),
    ('L-075679EF', 'Bridges', count('mediaconnect', 'list_bridges', 'Bridges')),
    ('L-CB77E87E', 'Outputs', outputs_per_flow),
    ('L-77138741', 'RouterInputs',
     lambda c: router_count(c, 'list_router_inputs', 'RouterInputs', ROUTER_IO_STATES)),
    ('L-58DF4801', 'RouterOutputs',
     lambda c: router_count(c, 'list_router_outputs', 'RouterOutputs', ROUTER_IO_STATES)),
    ('L-6C50CD26', 'RouterNetworkInterfaces',
     lambda c: router_count(c, 'list_router_network_interfaces',
                            'RouterNetworkInterfaces', ROUTER_INTERFACE_STATES)),
]


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
        entries.extend(context.run('mediaconnect', MEDIACONNECT_CHECKS, skip))
    if any(service == 'mediapackagev2' for service, _ in context.quotas):
        entries.extend(context.run('mediapackagev2', [
            ('L-A7040149', 'Channel Groups', count('mediapackagev2', 'list_channel_groups', 'ChannelGroups')),
            ('L-55777135', 'Channels per channel group', max_channels_per_group),
            ('L-305BEE26', 'Origin endpoints per channel', max_endpoints_per_channel),
        ], skip))
    return entries
