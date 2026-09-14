from unittest.mock import Mock

from modules.qmchecks.applicationsignals import CHECKS as APPLICATION_SIGNALS
from modules.qmchecks.logs import CHECKS as LOGS


def test_application_signals_counts_slos():
    ctx = Mock()
    ctx.call.return_value = [{'Arn': 'slo-1'}, {'Arn': 'slo-2'}]
    result = APPLICATION_SIGNALS[0][2](ctx)
    assert result['usage'] == 2
    assert result['source'].endswith('ListServiceLevelObjectives')


def test_logs_resource_policies_are_counted():
    ctx = Mock()
    ctx.call.return_value = [{'policyName': 'p'}]
    result = LOGS[1][2](ctx)
    assert result['usage'] == 1


def test_logs_filter_quotas_use_maximum_per_group():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'logGroupName': '/one'}, {'logGroupName': '/two'}],
        [{'filterName': 'a'}],
        [{'filterName': 'a'}, {'filterName': 'b'}, {'filterName': 'c'}],
    ]
    result = LOGS[2][2](ctx)
    assert (result['usage'], result['resource_id']) == (3, '/two')
