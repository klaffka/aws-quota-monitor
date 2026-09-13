from unittest.mock import Mock

from modules.qmchecks.auditmanager import CHECKS, controls_per_framework


def test_auditmanager_counts_custom_resources_and_running_assessments():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert CHECKS[0][2](ctx)['usage'] == 2
    assert CHECKS[1][2](ctx)['usage'] == 2
    assert CHECKS[2][2](ctx)['usage'] == 2


def test_auditmanager_controls_use_maximum_per_framework():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'framework-1'}, {'id': 'framework-2'}],
        {'framework': {'controlSets': [{'controls': [{'id': 'a'}]}]}},
        {'framework': {'controlSets': [{'controls': [{'id': 'a'}, {'id': 'b'}]}]}},
    ]
    result = controls_per_framework(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'framework-2')
