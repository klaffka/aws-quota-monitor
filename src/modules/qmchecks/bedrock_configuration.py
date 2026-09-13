"""Bedrock configuration maxima across working drafts and published versions."""
from functools import partial

from modules.qmcore.aws import NoData, maximum


def required_id(item, field='id'):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'Bedrock inventory is missing {field}')
    return value


def versions(items, parent):
    result = set()
    for item in items:
        if item.get('id') != parent:
            raise NoData('Bedrock version inventory contains a different parent')
        version = item.get('version')
        if version == 'DRAFT':
            continue
        if not isinstance(version, str) or not version.isascii() or not version.isdecimal() or int(version) < 1:
            raise NoData('Bedrock inventory has an unknown version')
        result.add(version)
    return sorted(result, key=int)


def flow_definitions(ctx):
    for flow in ctx.call('bedrock-agent', 'list_flows', 'flowSummaries'):
        fid = required_id(flow)
        published = versions(ctx.call('bedrock-agent', 'list_flow_versions', 'flowVersionSummaries',
                                      flowIdentifier=fid), fid)
        for version in ['DRAFT', *published]:
            if version == 'DRAFT':
                config = ctx.call('bedrock-agent', 'get_flow', flowIdentifier=fid, includedData='ALL_DATA')
            else:
                config = ctx.call('bedrock-agent', 'get_flow_version', flowIdentifier=fid,
                                  flowVersion=version, includedData='ALL_DATA')
            if config.get('id') != fid or config.get('version') != version:
                raise NoData('Bedrock flow response has a different identity or version')
            definition = config.get('definition')
            if not isinstance(definition, dict) or not isinstance(definition.get('nodes'), list):
                raise NoData('Bedrock flow response has no complete node definition')
            nodes = definition['nodes']
            if any(not isinstance(node.get('type'), str) for node in nodes):
                raise NoData('Bedrock flow node has no type')
            if any(node['type'] == 'Loop' for node in nodes):
                raise NoData('Quota scope for nodes inside a Bedrock Loop is not yet verified')
            yield f'{fid}/version/{version}', nodes


def flow_nodes(ctx, node_type=None, conditions=False):
    values = []
    for identity, nodes in flow_definitions(ctx):
        if conditions:
            for node in nodes:
                if node['type'] != 'Condition':
                    continue
                config = (node.get('configuration') or {}).get('condition') or {}
                entries = config.get('conditions')
                if not isinstance(entries, list):
                    raise NoData('Bedrock condition node has no condition list')
                values.append((f"{identity}/node/{required_id(node, 'name')}", len(entries), None))
        else:
            selected = nodes if node_type is None else [node for node in nodes if node['type'] == node_type]
            if node_type in {'Storage', 'Retrieval'}:
                for node in selected:
                    service = ((node.get('configuration') or {}).get(node_type.lower()) or {}).get('serviceConfiguration')
                    if not isinstance(service, dict) or set(service) != {'s3'}:
                        raise NoData('Bedrock storage/retrieval node has no verified S3 configuration')
            values.append((identity, len(selected), None))
    return maximum(values, 'FlowConditionNode' if conditions else 'FlowVersion',
                   'bedrock:GetFlow+GetFlowVersion')


def guardrail_versions(ctx, gid):
    return versions(ctx.call('bedrock', 'list_guardrails', 'guardrails', guardrailIdentifier=gid), gid)


def guardrail_definitions(ctx):
    for guardrail in ctx.call('bedrock', 'list_guardrails', 'guardrails'):
        gid = required_id(guardrail)
        for version in ['DRAFT', *guardrail_versions(ctx, gid)]:
            config = ctx.call('bedrock', 'get_guardrail', guardrailIdentifier=gid, guardrailVersion=version)
            if config.get('guardrailId') != gid or config.get('version') != version:
                raise NoData('Bedrock guardrail response has a different identity or version')
            yield f'{gid}/version/{version}', config


def policy_items(config, policy, field):
    if policy not in config:
        return []  # Policies are optional; an absent policy uses no entries.
    value = config[policy]
    if not isinstance(value, dict) or not isinstance(value.get(field, []), list):
        raise NoData('Bedrock guardrail policy has an invalid list')
    if policy in {'topicPolicy', 'automatedReasoningPolicy'} and field not in value:
        raise NoData('Bedrock guardrail policy is missing its required list')
    return value.get(field, [])


def guardrail_configuration(ctx, policy, field, measure=None):
    values = []
    for identity, config in guardrail_definitions(ctx):
        entries = policy_items(config, policy, field)
        if measure is None:
            values.append((identity, len(entries), None))
        else:
            for index, entry in enumerate(entries):
                value = entry.get(measure, [] if measure == 'examples' else None)
                expected = list if measure == 'examples' else str
                if not isinstance(value, expected):
                    raise NoData('Bedrock guardrail entry is missing its measured configuration')
                # Keep sensitive policy contents out of measurement metadata.
                values.append((f'{identity}/{field}/{index}', len(value), None))
    return maximum(values, 'GuardrailConfiguration', 'bedrock:GetGuardrail')


def version_count(ctx, resource):
    service, method, key, parameter = (
        ('bedrock', 'list_guardrails', 'guardrails', 'guardrailIdentifier') if resource == 'Guardrail'
        else ('bedrock-agent', 'list_prompts', 'promptSummaries', 'promptIdentifier'))
    values = []
    for parent in ctx.call(service, method, key):
        identity = required_id(parent)
        items = ctx.call(service, method, key, **{parameter: identity})
        values.append((identity, len(versions(items, identity)), None))
    return maximum(values, resource, f'{service}:{method}')


def profile_endpoints(ctx):
    values = []
    for profile in ctx.call('bedrock', 'list_inference_profiles', 'inferenceProfileSummaries'):
        identity = required_id(profile, 'inferenceProfileArn')
        models = profile.get('models')
        if not isinstance(models, list) or not models:
            raise NoData('Bedrock inference profile has no resolved model endpoints')
        # Different regional ARNs are distinct endpoints even for the same model.
        endpoints = {required_id(model, 'modelArn') for model in models}
        values.append((identity, len(endpoints), None))
    return maximum(values, 'InferenceProfile', 'bedrock:ListInferenceProfiles')


FLOW_QUOTAS = [
    ('L-E211B5EA', None), ('L-83D7FD1C', 'Agent'), ('L-8175E285', 'InlineCode'),
    ('L-7847F21F', 'Storage'), ('L-0F2A24D7', 'Prompt'), ('L-32F1CE34', 'Collector'),
    ('L-39128CD1', 'Condition'), ('L-8DBDC30B', 'Lex'), ('L-B536331C', 'Iterator'),
    ('L-08D49FA4', 'Input'), ('L-517574A2', 'KnowledgeBase'), ('L-A9C9E017', 'LambdaFunction'),
    ('L-CCB99FFA', 'Output'), ('L-17987C44', 'Retrieval'),
]
GUARDRAIL_QUOTAS = [
    ('L-85DABFD4', 'Words per word policy', 'wordPolicy', 'words', None),
    ('L-DF49A520', 'Word length in characters', 'wordPolicy', 'words', 'text'),
    ('L-6CA39F00', 'Topics per guardrail', 'topicPolicy', 'topics', None),
    ('L-99EDA841', 'Example phrases per topic', 'topicPolicy', 'topics', 'examples'),
    ('L-4F4FC597', 'Regex entities in sensitive information filter', 'sensitiveInformationPolicy', 'regexes', None),
    ('L-6F08AA6D', 'Regex length in characters', 'sensitiveInformationPolicy', 'regexes', 'pattern'),
    ('L-81F241B6', 'Automated Reasoning policies per guardrail', 'automatedReasoningPolicy', 'policies', None),
]
CHECKS = [(code, f'{kind or "Total"} nodes per flow', partial(flow_nodes, node_type=kind))
          for code, kind in FLOW_QUOTAS]
CHECKS += [(code, name, partial(guardrail_configuration, policy=policy, field=field, measure=measure))
           for code, name, policy, field, measure in GUARDRAIL_QUOTAS]
CHECKS += [
    ('L-2D84F8A3', 'Conditions per condition node', partial(flow_nodes, conditions=True)),
    ('L-D471AEAB', 'Versions per guardrail', partial(version_count, resource='Guardrail')),
    ('L-FBBE47CA', 'Versions per prompt', partial(version_count, resource='Prompt')),
    ('L-77D5E75F', 'Endpoints per inference profile', profile_endpoints),
]
