from unittest.mock import Mock

from modules.qmchecks.mediastore import CHECKS as STORE
from modules.qmchecks.mediatailor import CHECKS as TAILOR
from modules.qmchecks.kinesisvideo import CHECKS as VIDEO


def test_media_service_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'container'}], [{'Name': 'location'}], [{'Name': 'channel'}],
                            [{'StreamName': 'stream'}], [{'ChannelName': 'signaling'}],
                            [{'StreamName': 'retained', 'DataRetentionInHours': 1}]]
    assert STORE[0][2](ctx)['usage'] == 1
    assert [check[2](ctx)['usage'] for check in TAILOR] == [1, 1]
    assert [check[2](ctx)['usage'] for check in VIDEO] == [1, 1, 1]


def test_kinesisvideo_media_storage_channels_filter_retention():
    ctx = Mock()
    ctx.call.return_value = [
        {'StreamName': 'retained', 'DataRetentionInHours': 24},
        {'StreamName': 'live-only', 'DataRetentionInHours': 0},
        {'StreamName': 'unset'},
    ]
    check = next(check for check in VIDEO if check[0] == 'L-B71421B8')
    assert check[2](ctx)['usage'] == 1
