from datetime import datetime, timedelta, UTC
from unittest.mock import Mock

import pytest

from modules.qmchecks.bedrock_agentcore import generated_policies
from modules.qmcore.aws import NoData

NOW = datetime(2026, 9, 15, tzinfo=UTC)


def generation(days_ago):
    return {'policyGenerationId': f'gen-{days_ago}',
            'createdAt': NOW - timedelta(days=days_ago)}


def test_only_generations_inside_the_rolling_window_are_counted():
    ctx = Mock()
    ctx.now = NOW

    def call(_service, method, _key=None, **kwargs):
        if method == 'list_policy_engines':
            return [{'policyEngineId': 'first'}, {'policyEngineId': 'second'}]
        if kwargs['policyEngineId'] == 'first':
            return [generation(1), generation(6), generation(8)]
        return [generation(2)]

    ctx.call.side_effect = call
    result = generated_policies(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'first')


def test_a_generation_without_a_creation_time_raises_nodata():
    ctx = Mock()
    ctx.now = NOW
    ctx.call.side_effect = [[{'policyEngineId': 'first'}],
                            [{'policyGenerationId': 'gen-1'}]]
    with pytest.raises(NoData, match='no creation time'):
        generated_policies(ctx)
