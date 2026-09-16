from unittest.mock import Mock

from modules.qmchecks.mediaconvert import CHECKS as MEDIA_CHECKS
from modules.qmchecks.ivs import CHECKS as IVS_CHECKS


def test_mediaconvert_resource_counts():
    # The plain inventories; the queue occupancy and preset checks read a field
    # of each entry and are covered by tests/test_mediaconvert_and_transfer_scopes.py.
    ctx = Mock()
    ctx.call.side_effect = [[{}], [{}, {}]]
    counted = ['L-44E8E4BC', 'L-FFA964F8']
    by_code = {code: fn for code, _, fn in MEDIA_CHECKS}
    assert [by_code[code](ctx)['usage'] for code in counted] == [1, 2]


def test_ivs_resource_counts():
    # The plain inventories; the composition, stream key and participant checks
    # read a state or a parent resource and have their own tests.
    ctx = Mock()
    ctx.call.side_effect = [[{}, {}], [{}], [{}], [{}, {}], [{}]]
    counted = ['L-C01DFF58', 'L-90ABAB37', 'L-BF843A02', 'L-F7C5B6C9', 'L-CE6ADDBE']
    by_code = {code: fn for code, _, fn in IVS_CHECKS}
    assert [by_code[code](ctx)['usage'] for code in counted] == [2, 1, 1, 2, 1]
