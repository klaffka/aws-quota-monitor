from unittest.mock import Mock

from modules.qmchecks.mediaconvert import CHECKS as MEDIA_CHECKS
from modules.qmchecks.ivs import CHECKS as IVS_CHECKS


def test_mediaconvert_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}], [{}, {}]]
    assert [fn(ctx)['usage'] for _, _, fn in MEDIA_CHECKS] == [1, 2]


def test_ivs_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}, {}], [{}], [{}], [{}, {}], [{}]]
    assert [fn(ctx)['usage'] for _, _, fn in IVS_CHECKS] == [2, 1, 1, 2, 1]
