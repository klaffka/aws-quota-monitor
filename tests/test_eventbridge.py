from unittest.mock import Mock

from modules.qmchecks.eventbridge import resource_count


def test_eventbridge_resource_inventories_are_counted():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Name': 'default'}, {'Name': 'custom'}],
        [{'Name': 'rule-one'}],
    ]
    assert resource_count(ctx, 'list_event_buses', 'EventBuses')['usage'] == 2
    assert resource_count(ctx, 'list_rules', 'Rules')['usage'] == 1
