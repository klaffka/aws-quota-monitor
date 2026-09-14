from unittest.mock import Mock

from modules.qmchecks.bedrock import (
    action_groups_per_agent,
    aliases_per_agent,
    aliases_per_flow,
    data_sources_per_knowledge_base,
    knowledge_bases_per_agent,
    versions_per_flow,
)


def test_bedrock_nested_resource_counts_use_parent_scoped_paginated_apis():
    ctx = Mock()

    def call(_service, method, key=None, **kwargs):
        if method == 'list_knowledge_bases':
            return [{'knowledgeBaseId': 'kb-1'}]
        if method == 'list_data_sources':
            return [{'dataSourceId': 'ds-1'}, {'dataSourceId': 'ds-2'}]
        if method == 'list_agents':
            return [{'agentId': 'agent-1'}]
        if method == 'list_agent_aliases':
            return [{'agentAliasId': 'alias-1'}]
        if method == 'list_agent_action_groups':
            return [{'actionGroupState': 'ENABLED'}, {'actionGroupState': 'DISABLED'}]
        if method == 'list_agent_knowledge_bases':
            return [{'knowledgeBaseId': 'kb-1'}]
        if method == 'list_flows':
            return [{'id': 'flow-1'}]
        if method == 'list_flow_aliases':
            return [{'id': 'alias-1'}]
        if method == 'list_flow_versions':
            return [{'id': 'v1'}, {'id': 'v2'}]
        raise AssertionError((method, key, kwargs))

    ctx.call.side_effect = call
    assert data_sources_per_knowledge_base(ctx)['usage'] == 2
    assert aliases_per_agent(ctx)['usage'] == 1
    assert action_groups_per_agent(ctx)['usage'] == 2
    assert action_groups_per_agent(ctx, enabled=True)['usage'] == 1
    assert knowledge_bases_per_agent(ctx)['usage'] == 1
    assert aliases_per_flow(ctx)['usage'] == 1
    assert versions_per_flow(ctx)['usage'] == 2
