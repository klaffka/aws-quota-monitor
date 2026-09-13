from unittest.mock import Mock

from modules.qmchecks.cases import CHECKS


def test_cases_rules_are_counted_per_domain():
    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': 'domain'}],
                            [{'caseRuleId': 'rule', 'ruleType': 'Required'}]]
    result = CHECKS[2][2](ctx)
    assert (result['usage'], result['resource_id']) == (1, 'domain')
