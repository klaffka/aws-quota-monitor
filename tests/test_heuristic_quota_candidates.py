from unittest.mock import Mock

from modules.qmchecks.amplifyuibuilder import CHECKS as UI_CHECKS
from modules.qmchecks.acm import CHECKS as ACM_CHECKS
from modules.qmchecks.databrew import CHECKS as DATABREW_CHECKS
from modules.qmchecks.evs import CHECKS as EVS_CHECKS
from modules.qmchecks.eventbridge import CHECKS as EVENT_CHECKS


def test_databrew_resource_counts_use_paginated_lists():
    # The plain account inventories; the ruleset, project and recipe scopes read
    # a field of each entry and are covered by
    # tests/test_databrew_and_wellarchitected_scopes.py.
    ctx = Mock()
    ctx.call.return_value = [{}]
    plain = ['L-CE9E9D8D', 'L-940C8930', 'L-955A1FA6', 'L-BF3E0A94', 'L-EE2782A4',
             'L-0D2C4DFC']
    by_code = {code: fn for code, _name, fn in DATABREW_CHECKS}
    assert [by_code[code](ctx)['usage'] for code in plain] == [1] * len(plain)


def test_amplify_ui_resources_are_maximum_per_app_and_environment():
    ctx = Mock()
    ctx.call.side_effect = [[{'appId': 'a'}], [{'environmentName': 'staging'}],
                            [{'id': 'theme'}]]
    result = UI_CHECKS[0][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'a/staging')


def test_evs_environments_and_hosts_are_counted():
    ctx = Mock()
    ctx.call.return_value = [{'environmentId': 'env'}]
    assert EVS_CHECKS[0][2](ctx)['usage'] == 1
    ctx.call.side_effect = [[{'environmentId': 'env'}], [{'hostId': 'host'}]]
    assert EVS_CHECKS[1][2](ctx)['usage'] == 1


def test_acm_imported_certificates_are_counted_by_certificate_type():
    ctx = Mock()
    ctx.call.return_value = [{'Type': 'IMPORTED'}, {'Type': 'AMAZON_ISSUED'}, {'Type': 'IMPORTED'}]
    assert ACM_CHECKS[1][2](ctx)['usage'] == 2


def test_eventbridge_targets_are_maximum_per_rule():
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'rule'}], [{'Id': 'target-1'}, {'Id': 'target-2'}]]
    result = EVENT_CHECKS[2][2](ctx)
    assert (result['usage'], result['resource_id']) == (2, 'rule')
