from unittest.mock import Mock

from modules.qmchecks.dms_resources import CHECKS as DMS
from modules.qmchecks.mgn import CHECKS as MGN


# The scoped checks group or filter their inventory; they are covered by
# tests/test_dms_migrations.py against a real client.
SCOPED = {'L-4182EDE9', 'L-62EFB27A', 'L-FBEA20FB'}


def test_dms_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'resource'}]
    totals = [check[2](ctx)['usage'] for check in DMS if check[0] not in SCOPED]
    assert totals == [1] * (len(DMS) - len(SCOPED))


def test_dms_inventory_checks_cover_subnet_groups_projects_and_data_providers():
    codes = {code for code, _, _ in DMS}
    assert {'L-27B24FAD', 'L-DE63148C', 'L-9A47CA81',
            'L-1AB41EE0', 'L-D12045C2'} <= codes


def test_mgn_counts_only_non_archived_applications():
    ctx = Mock()
    ctx.call.return_value = [{'applicationID': 'a', 'isArchived': False},
                             {'applicationID': 'b', 'isArchived': True}]
    by_code = {code: check for code, _, check in MGN}
    assert by_code['L-D5507441'](ctx)['usage'] == 1
    assert by_code['L-391504A2'](ctx)['usage'] == 1
