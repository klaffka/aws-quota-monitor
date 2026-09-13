from unittest.mock import Mock

from modules.qmchecks.dms_resources import CHECKS as DMS
from modules.qmchecks.mgn import CHECKS as MGN


def test_dms_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'resource'}]
    assert [check[2](ctx)['usage'] for check in DMS] == [1] * len(DMS)


def test_dms_inventory_checks_cover_subnet_groups_projects_and_data_providers():
    codes = {code for code, _, _ in DMS}
    assert {'L-27B24FAD', 'L-DE63148C', 'L-9A47CA81',
            'L-1AB41EE0', 'L-D12045C2'} <= codes


def test_mgn_counts_only_non_archived_applications():
    ctx = Mock()
    ctx.call.return_value = [{'applicationID': 'a'}, {'applicationID': 'b', 'isArchived': True}]
    assert MGN[0][2](ctx)['usage'] == 1
