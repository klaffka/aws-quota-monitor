from unittest.mock import Mock

from modules.qmchecks.config_service import CHECKS


def test_config_rules_are_counted_from_regional_inventory():
    ctx = Mock()
    ctx.call.return_value = [{'ConfigRuleName': 'rule-one'}, {'ConfigRuleName': 'rule-two'}]
    assert CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.args[:3] == ('config', 'describe_config_rules', 'ConfigRules')
