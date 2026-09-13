from unittest.mock import Mock

from modules.qmchecks.media_extra import get_current_quotastatus_media_extra


def test_media_connect_counts():
    ctx = Mock(quotas={('mediaconnect', 'L-F1F62F5D'): {}, ('mediaconnect', 'L-A99016A8'): {}, ('mediaconnect', 'L-075679EF'): {}})
    ctx.call.side_effect = [[{}], [{}, {}], [{}]]
    ctx.run.side_effect = lambda service, checks, skip: [
        {'quotaCode': code, 'usageValue': fn(ctx)['usage']} for code, _, fn in checks]
    assert [x['usageValue'] for x in get_current_quotastatus_media_extra(ctx=ctx)] == [1, 2, 1]


def test_media_package_v2_parent_scoped_counts():
    from modules.qmchecks.media_extra import max_channels_per_group, max_endpoints_per_channel
    ctx = Mock()
    ctx.call.return_value = [{'ChannelGroupName': 'g1'}]
    # The group contains two channels.
    ctx.call.side_effect = [[{'ChannelGroupName': 'g1'}], [{}, {}]]
    assert max_channels_per_group(ctx)['usage'] == 2
    # The same group has one channel with three endpoints.
    ctx.call.side_effect = [[{'ChannelGroupName': 'g1'}], [{'ChannelName': 'c1'}], [{}, {}, {}]]
    assert max_endpoints_per_channel(ctx)['usage'] == 3
