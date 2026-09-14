from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks import networkinsights
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


class NetworkInsightsContext:
    def __init__(self):
        self.data = {
            'describe_network_insights_access_scope_analyses': [
                {'NetworkInsightsAccessScopeAnalysisId': 'scope-analysis/a',
                 'Status': 'running'},
                {'NetworkInsightsAccessScopeAnalysisId': 'scope-analysis/b',
                 'Status': 'succeeded'},
                {'NetworkInsightsAccessScopeAnalysisId': 'scope-analysis/c',
                 'Status': 'running'},
            ],
            'describe_network_insights_analyses': [
                {'NetworkInsightsAnalysisId': 'analysis/a', 'Status': 'failed'},
                {'NetworkInsightsAnalysisId': 'analysis/b', 'Status': 'running'},
            ],
            'describe_network_insights_paths': [
                {'NetworkInsightsPathId': 'path/a'},
                {'NetworkInsightsPathId': 'path/b'},
            ],
            'describe_network_insights_access_scopes': [
                {'NetworkInsightsAccessScopeId': 'scope/a'},
            ],
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'ec2'
        assert not kwargs
        return self.data[method]


def test_network_insights_counts_retained_and_running_analyses():
    ctx = NetworkInsightsContext()

    assert networkinsights.account_count(
        ctx, **networkinsights.ACCESS_SCOPE_ANALYSES)['usage'] == 3
    assert networkinsights.concurrent_count(
        ctx, **networkinsights.ACCESS_SCOPE_ANALYSES)['usage'] == 2
    assert networkinsights.account_count(
        ctx, **networkinsights.REACHABILITY_ANALYSES)['usage'] == 2
    assert networkinsights.concurrent_count(
        ctx, **networkinsights.REACHABILITY_ANALYSES)['usage'] == 1


def test_network_insights_counts_paths_and_access_scopes():
    ctx = NetworkInsightsContext()

    results = {code: check(ctx)['usage'] for code, _name, check in networkinsights.CHECKS}
    assert results['L-51CB2D5B'] == 2
    assert results['L-72DF2E0E'] == 1


def test_network_insights_rejects_conflicting_pages_and_unknown_states():
    ctx = NetworkInsightsContext()
    ctx.data['describe_network_insights_analyses'].append(
        {'NetworkInsightsAnalysisId': 'analysis/a', 'Status': 'succeeded'})
    with pytest.raises(NoData, match='changed during pagination'):
        networkinsights.account_count(ctx, **networkinsights.REACHABILITY_ANALYSES)

    ctx = NetworkInsightsContext()
    ctx.data['describe_network_insights_access_scope_analyses'][0]['Status'] = 'pending'
    with pytest.raises(NoData, match='unknown status'):
        networkinsights.concurrent_count(ctx, **networkinsights.ACCESS_SCOPE_ANALYSES)


def test_network_insights_checks_are_registered_selected_and_permitted():
    assert {('networkinsights', code) for code, _name, _check
            in networkinsights.CHECKS} <= custom_keys()

    context = Mock(quotas={('networkinsights', 'L-51CB2D5B'): {}})
    context.run.return_value = []
    assert networkinsights.get_current_quotastatus_networkinsights(ctx=context) == []
    assert context.run.call_args.args[1] == networkinsights.CHECKS

    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in (
        'DescribeNetworkInsightsAccessScopes',
        'DescribeNetworkInsightsAccessScopeAnalyses',
        'DescribeNetworkInsightsPaths',
        'DescribeNetworkInsightsAnalyses',
    ):
        assert f'"ec2:{action}"' in policy
