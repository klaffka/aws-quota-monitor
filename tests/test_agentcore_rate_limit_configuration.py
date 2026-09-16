from unittest.mock import Mock

import pytest

from modules.qmchecks.bedrock_agentcore import rate_limit_configuration
from modules.qmcore.aws import NoData


def test_rate_limit_field_maxima_are_scoped_across_all_gateways():
    ctx = Mock()
    def call(service, method, key, **kwargs):
        if method == 'list_gateways':
            return [{'gatewayId': 'first'}, {'gatewayId': 'second'}]
        if kwargs['gatewayIdentifier'] == 'first':
            return [{'rateLimitId': 'same', 'entries': [{}, {}, {}], 'dimensionKeys': ['targetName']}]
        return [{'rateLimitId': 'same', 'entries': [{}], 'dimensionKeys': ['targetName', 'toolName']}]
    ctx.call.side_effect = call
    entries = rate_limit_configuration(ctx, 'entries')
    dimensions = rate_limit_configuration(ctx, 'dimensionKeys')
    assert entries['usage'] == 3
    assert entries['resource_id'] == 'first/same'
    assert dimensions['usage'] == 2
    assert dimensions['resource_id'] == 'second/same'
    assert all(call.args[1] in {'list_gateways', 'list_gateway_rate_limits'} for call in ctx.call.call_args_list)


def test_missing_configuration_field_is_not_reported_as_empty():
    ctx = Mock()
    ctx.call.side_effect = [[{'gatewayId': 'gateway'}], [{'rateLimitId': 'limit'}]]
    with pytest.raises(NoData, match='dimensionKeys'):
        rate_limit_configuration(ctx, 'dimensionKeys')
