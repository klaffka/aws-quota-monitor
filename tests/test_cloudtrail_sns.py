from unittest.mock import Mock

from modules.qmchecks.cloudtrail import resource_count as cloudtrail_count
from modules.qmchecks.sns import CHECKS


def test_cloudtrail_resource_inventories_are_counted():
    ctx = Mock()
    ctx.call.side_effect = [
            [{'Name': 'trail-one'}],
            [{'EventDataStoreArn': 'arn:store'}],
            [{'ChannelArn': 'arn:channel'}],
            [{'DashboardArn': 'arn:dashboard'}],
    ]
    assert cloudtrail_count(ctx, 'describe_trails', 'trailList')['usage'] == 1
    assert cloudtrail_count(ctx, 'list_event_data_stores', 'EventDataStores')['usage'] == 1
    assert cloudtrail_count(ctx, 'list_channels', 'Channels')['usage'] == 1
    assert cloudtrail_count(ctx, 'list_dashboards', 'Dashboards')['usage'] == 1


def test_sns_topic_check_uses_paginated_list_topics():
    ctx = Mock()
    ctx.call.return_value = [{'TopicArn': 'arn:one'}, {'TopicArn': 'arn:two'}]
    result = CHECKS[0][2](ctx)
    assert result['usage'] == 2
    assert ctx.call.call_args.args[:3] == ('sns', 'list_topics', 'Topics')
