"""Amazon Bedrock knowledge-base inventory."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env
from modules.qmchecks.bedrock_batch import CHECKS as BATCH_CHECKS
from modules.qmchecks.bedrock_configuration import CHECKS as CONFIGURATION_CHECKS
from modules.qmchecks.bedrock_reasoning import CHECKS as REASONING_CHECKS
from modules.qmchecks.bedrock_evaluation import CHECKS as EVALUATION_CHECKS
from modules.qmchecks.bedrock_data_automation import CHECKS as DATA_AUTOMATION_CHECKS


def _max_nested(ctx, parents, parent_field, method, key, kwargs=None,
                request_field=None,
                resource_type='BedrockResource', source=None, predicate=None):
    values = []
    for parent in parents(ctx):
        parent_id = parent.get(parent_field)
        if not parent_id:
            continue
        call_kwargs = dict(kwargs or {})
        call_kwargs[request_field or parent_field] = parent_id
        items = ctx.call('bedrock-agent', method, key, **call_kwargs)
        if predicate:
            items = [item for item in items if predicate(item)]
        values.append((parent_id, len(items), None))
    return maximum(values, resource_type, source or f'bedrock-agent:{method}')


def data_sources_per_knowledge_base(ctx):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_knowledge_bases', 'knowledgeBaseSummaries'),
                       'knowledgeBaseId', 'list_data_sources', 'dataSourceSummaries',
                       resource_type='KnowledgeBase', source='bedrock-agent:ListKnowledgeBases+ListDataSources')


def aliases_per_agent(ctx):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_agents', 'agentSummaries'),
                       'agentId', 'list_agent_aliases', 'agentAliasSummaries',
                       resource_type='Agent', source='bedrock-agent:ListAgents+ListAgentAliases')


def action_groups_per_agent(ctx, enabled=False):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_agents', 'agentSummaries'),
                       'agentId', 'list_agent_action_groups', 'actionGroupSummaries',
                       kwargs={'agentVersion': 'DRAFT'}, resource_type='Agent',
                       source='bedrock-agent:ListAgents+ListAgentActionGroups',
                       predicate=(lambda item: item.get('actionGroupState') == 'ENABLED') if enabled else None)


def knowledge_bases_per_agent(ctx):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_agents', 'agentSummaries'),
                       'agentId', 'list_agent_knowledge_bases', 'agentKnowledgeBaseSummaries',
                       kwargs={'agentVersion': 'DRAFT'}, resource_type='Agent',
                       source='bedrock-agent:ListAgents+ListAgentKnowledgeBases')


def aliases_per_flow(ctx):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_flows', 'flowSummaries'),
                       'id', 'list_flow_aliases', 'flowAliasSummaries', request_field='flowIdentifier',
                       resource_type='Flow', source='bedrock-agent:ListFlows+ListFlowAliases')


def versions_per_flow(ctx):
    return _max_nested(ctx, lambda c: c.call('bedrock-agent', 'list_flows', 'flowSummaries'),
                       'id', 'list_flow_versions', 'flowVersionSummaries', request_field='flowIdentifier',
                       resource_type='Flow', source='bedrock-agent:ListFlows+ListFlowVersions')


def blueprint_count(ctx):
    arns = set()
    for item in ctx.call('bedrock-data-automation', 'list_blueprints', 'blueprints',
                         resourceOwner='ACCOUNT', blueprintStageFilter='ALL'):
        arn = item.get('blueprintArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Bedrock blueprint inventory has no ARN')
        arns.add(arn)
    return dict(usage=len(arns), source='bedrock-data-automation:ListBlueprints', method='ACCOUNT_COUNT')


CHECKS = [('L-60DA3E0D', 'Knowledge bases per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock-agent', 'list_knowledge_bases', 'knowledgeBaseSummaries')),
                            source='bedrock-agent:ListKnowledgeBases', method='ACCOUNT_COUNT')),
          ('L-97D79C54', 'Agents per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock-agent', 'list_agents', 'agentSummaries')),
                            source='bedrock-agent:ListAgents', method='ACCOUNT_COUNT')),
          ('L-D321719B', 'Flows per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock-agent', 'list_flows', 'flowSummaries')),
                            source='bedrock-agent:ListFlows', method='ACCOUNT_COUNT')),
          ('L-CB5B847D', 'Custom models per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock', 'list_custom_models', 'modelSummaries')),
                            source='bedrock:ListCustomModels', method='ACCOUNT_COUNT')),
          ('L-0E5A840C', 'Guardrails per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock', 'list_guardrails', 'guardrails')),
                            source='bedrock:ListGuardrails', method='ACCOUNT_COUNT')),
          ('L-45B04988', 'Imported models per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock', 'list_imported_models', 'modelSummaries')),
                            source='bedrock:ListImportedModels', method='ACCOUNT_COUNT')),
          ('L-40EC9882', 'Inference profiles per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock', 'list_inference_profiles', 'inferenceProfileSummaries')),
                            source='bedrock:ListInferenceProfiles', method='ACCOUNT_COUNT')),
          ('L-B783C50B', 'Prompts per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock-agent', 'list_prompts', 'promptSummaries')),
                            source='bedrock-agent:ListPrompts', method='ACCOUNT_COUNT')),
          ('L-23CF4444', 'Maximum blueprints per account',
           blueprint_count),
          ('L-DAF06DBA', 'Automated Reasoning policies per account',
           lambda ctx: dict(usage=len(ctx.call('bedrock', 'list_automated_reasoning_policies',
                                               'automatedReasoningPolicySummaries')),
                            source='bedrock:ListAutomatedReasoningPolicies', method='ACCOUNT_COUNT')),
          ('L-679D8304', 'Data sources per knowledge base', data_sources_per_knowledge_base),
          ('L-6E57E827', 'Associated aliases per Agent', aliases_per_agent),
          ('L-5DAAE567', 'Action groups per Agent', action_groups_per_agent),
          ('L-14A16430', 'Enabled action groups per agent',
           lambda ctx: action_groups_per_agent(ctx, enabled=True)),
          ('L-13143995', 'Associated knowledge bases per Agent', knowledge_bases_per_agent),
          ('L-130570F3', 'Flow aliases per flow', aliases_per_flow),
          ('L-60AFC764', 'Flow versions per flow', versions_per_flow)]


EXTENDED_CHECKS = BATCH_CHECKS + CONFIGURATION_CHECKS + REASONING_CHECKS + EVALUATION_CHECKS + DATA_AUTOMATION_CHECKS
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_bedrock(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'bedrock' for service, _ in context.quotas): return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS if ('bedrock', check[0]) in context.quotas]
    return context.run('bedrock', checks, skip)
