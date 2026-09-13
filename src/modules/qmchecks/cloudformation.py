"""CloudFormation regional stack and private registry inventory."""
import json
import re
from functools import partial

import yaml

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


class CloudFormationLoader(yaml.SafeLoader):
    """Safe YAML loader that preserves values behind CloudFormation short tags."""


def construct_intrinsic(loader, _tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    raise NoData('CloudFormation template contains an unknown YAML node')


CloudFormationLoader.add_multi_constructor('!', construct_intrinsic)
DYNAMIC_REFERENCE = re.compile(r'\{\{resolve:[^{}]+}}')


def stacks(ctx):
    summaries = ctx.call('cloudformation', 'list_stacks', 'StackSummaries')
    # DELETE_COMPLETE stacks are retained for history by the API but do not
    # consume the regional stack quota.
    return [stack for stack in summaries if stack.get('StackStatus') != 'DELETE_COMPLETE']


def stack_sets(ctx):
    result = {}
    for item in ctx.call('cloudformation', 'list_stack_sets', 'Summaries', Status='ACTIVE'):
        identity = item.get('StackSetId') or item.get('StackSetName')
        if not isinstance(identity, str) or not identity or item.get('Status') not in {None, 'ACTIVE'}:
            raise NoData('CloudFormation stack set inventory has an invalid identity or status')
        if identity in result and result[identity] != item:
            raise NoData('CloudFormation stack set changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def types(ctx, type_name):
    items = ctx.call('cloudformation', 'list_types', 'TypeSummaries', Type=type_name,
                     Visibility='PRIVATE', DeprecatedStatus='LIVE')
    # PRIVATE visibility also returns activated public extensions. IsActivated
    # distinguishes those from extensions registered privately in this account.
    result = {}
    for item in items:
        if item.get('IsActivated') is True:
            continue
        name = required_id(item, 'TypeName')
        if item.get('Type', type_name) != type_name:
            raise NoData('CloudFormation type inventory returned another extension kind')
        if name in result and result[name] != item:
            raise NoData('CloudFormation type changed during pagination')
        result[name] = item
    return [result[name] for name in sorted(result)]


def required_id(item, field):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'CloudFormation type inventory is missing {field}')
    return value


def versions_per_type(ctx, type_name):
    values = []
    for item in types(ctx, type_name):
        name = required_id(item, 'TypeName')
        versions = set()
        for version in ctx.call('cloudformation', 'list_type_versions', 'TypeVersionSummaries',
                                Type=type_name, TypeName=name, DeprecatedStatus='LIVE'):
            if version.get('Type') != type_name or version.get('TypeName') != name:
                raise NoData('CloudFormation version belongs to another extension')
            versions.add(required_id(version, 'VersionId'))
        if not versions:
            raise NoData('Registered CloudFormation extension has no live version')
        values.append((name, len(versions), None))
    return maximum(values, f'CloudFormation{type_name.title()}',
                   'cloudformation:ListTypes+ListTypeVersions')


def template_stacks(ctx):
    result = {}
    for item in stacks(ctx):
        identity = item.get('StackId') or item.get('StackName')
        if not isinstance(identity, str) or not identity:
            raise NoData('CloudFormation stack inventory has no identity')
        if identity in result and result[identity] != item:
            raise NoData('CloudFormation stack changed during pagination')
        result[identity] = item
    return sorted(result)


def parse_template(body):
    if not isinstance(body, str) or not body.strip():
        raise NoData('CloudFormation GetTemplate returned no template body')
    try:
        template = json.loads(body)
    except json.JSONDecodeError:
        try:
            template = yaml.load(body, Loader=CloudFormationLoader)
        except yaml.YAMLError as exc:
            raise NoData('CloudFormation template is not valid JSON or YAML') from exc
    if not isinstance(template, dict):
        raise NoData('CloudFormation template is not an object')
    return template


def template_definitions(ctx, stage='Processed'):
    for identity in template_stacks(ctx):
        response = ctx.call('cloudformation', 'get_template', StackName=identity, TemplateStage=stage)
        stages = response.get('StagesAvailable')
        if stages is not None and (not isinstance(stages, list) or stage not in stages):
            raise NoData(f'CloudFormation stack has no {stage.lower()} template')
        body = response.get('TemplateBody')
        yield identity, body, parse_template(body)


def template_section(template, name, required=False):
    value = template.get(name, None if required else {})
    if not isinstance(value, dict) or (required and not value):
        raise NoData(f'CloudFormation template has an invalid {name} section')
    if any(not isinstance(key, str) or not key for key in value):
        raise NoData(f'CloudFormation template {name} section has an invalid name')
    return value


def mapping_details(template):
    mappings = template_section(template, 'Mappings')
    for name, mapping in mappings.items():
        if not isinstance(mapping, dict):
            raise NoData('CloudFormation mapping is not an object')
        names = [name]
        for key, attributes in mapping.items():
            if not isinstance(key, str) or not key or not isinstance(attributes, dict):
                raise NoData('CloudFormation mapping has an invalid attribute map')
            names.append(key)
            if any(not isinstance(attribute, str) or not attribute for attribute in attributes):
                raise NoData('CloudFormation mapping has an invalid nested attribute name')
            names.extend(attributes)
        yield name, mapping, names


def dynamic_reference_count(value):
    if isinstance(value, str):
        return len(DYNAMIC_REFERENCE.findall(value))
    if isinstance(value, list):
        return sum(dynamic_reference_count(item) for item in value)
    if isinstance(value, dict):
        return sum(dynamic_reference_count(key) + dynamic_reference_count(item)
                   for key, item in value.items())
    return 0


def template_measure(ctx, measure):
    values = []
    stage = 'Original' if measure == 'template_size' else 'Processed'
    for identity, body, template in template_definitions(ctx, stage):
        if measure in {'resources', 'parameters', 'outputs', 'mappings'}:
            section = measure.title()
            usage = len(template_section(template, section, required=measure == 'resources'))
        elif measure == 'mapping_attributes':
            entries = [(name, len(mapping)) for name, mapping, _ in mapping_details(template)]
            name, usage = max(entries, key=lambda item: item[1], default=(None, 0))
            if name is not None:
                identity = f'{identity}/mapping/{name}'
        elif measure == 'dynamic_references':
            # Count parsed scalar values so YAML comments cannot inflate usage.
            usage = dynamic_reference_count(template)
        elif measure == 'template_size':
            usage = len(body.encode('utf-8')) / (1024 * 1024)
        elif measure == 'description_length':
            description = template.get('Description', '')
            if not isinstance(description, str):
                raise NoData('CloudFormation template description is not text')
            usage = len(description.encode('utf-8'))
        elif measure == 'mapping_name_length':
            usage = max((len(name) for _, _, names in mapping_details(template) for name in names), default=0)
        else:
            section = {'resource_name_length': 'Resources', 'parameter_name_length': 'Parameters',
                       'output_name_length': 'Outputs'}[measure]
            names = template_section(template, section, required=section == 'Resources')
            usage = max((len(name) for name in names), default=0)
        values.append((identity, usage, None))
    result = maximum(values, 'CloudFormationTemplate', 'cloudformation:GetTemplate')
    if measure == 'template_size':
        result['unit'] = 'Megabytes'
    return result


def stack_set_details(ctx):
    result = []
    for summary in stack_sets(ctx):
        identity = summary.get('StackSetId') or summary.get('StackSetName')
        name = summary.get('StackSetName')
        if not isinstance(identity, str) or not identity or not isinstance(name, str) or not name:
            raise NoData('CloudFormation stack set inventory has no identity')
        response = ctx.call('cloudformation', 'describe_stack_set', StackSetName=name)
        detail = response.get('StackSet')
        detail_identity = detail.get('StackSetId') if isinstance(detail, dict) else None
        if not isinstance(detail, dict) or detail.get('StackSetName') != name \
                or detail_identity != identity or detail.get('Status') != 'ACTIVE':
            raise NoData('CloudFormation stack set detail is missing, deleted or mismatched')
        automatic = detail.get('AutoDeployment', {})
        if not isinstance(automatic, dict):
            raise NoData('CloudFormation stack set has invalid auto-deployment configuration')
        dependencies = automatic.get('DependsOn', [])
        if not isinstance(dependencies, list) or any(not isinstance(value, str) or not value
                                                      for value in dependencies):
            raise NoData('CloudFormation stack set has invalid dependencies')
        if len(set(dependencies)) != len(dependencies):
            raise NoData('CloudFormation stack set repeats a dependency')
        result.append((identity, name, dependencies))
    return result


def dependencies_per_stack_set(ctx):
    values = [(identity, len(dependencies), None)
              for identity, _, dependencies in stack_set_details(ctx)]
    return maximum(values, 'CloudFormationStackSet',
                   'cloudformation:ListStackSets+DescribeStackSet')


def queued_operations_per_stack_set(ctx):
    values = []
    statuses = {'RUNNING', 'SUCCEEDED', 'FAILED', 'STOPPING', 'STOPPED', 'QUEUED'}
    for summary in stack_sets(ctx):
        identity = summary.get('StackSetId') or summary.get('StackSetName')
        name = summary.get('StackSetName')
        if not isinstance(identity, str) or not identity or not isinstance(name, str) or not name:
            raise NoData('CloudFormation stack set inventory has no identity')
        operations = {}
        for operation in ctx.call('cloudformation', 'list_stack_set_operations', 'Summaries',
                                  StackSetName=name):
            operation_id = required_id(operation, 'OperationId')
            if operation.get('Status') not in statuses:
                raise NoData('CloudFormation stack set operation has an unknown status')
            if operation_id in operations and operations[operation_id] != operation:
                raise NoData('CloudFormation stack set operation changed during pagination')
            operations[operation_id] = operation
        values.append((identity, sum(item['Status'] == 'QUEUED' for item in operations.values()), None))
    return maximum(values, 'CloudFormationStackSet',
                   'cloudformation:ListStackSets+ListStackSetOperations')


def stack_instances_per_set(ctx):
    values = []
    for stack_set in stack_sets(ctx):
        name = stack_set.get('StackSetName')
        if name:
            values.append((name, len(ctx.call('cloudformation', 'list_stack_instances',
                                              'Summaries', StackSetName=name)), None))
    return maximum(values, 'CloudFormationStackSet', 'cloudformation:ListStackInstances')


CHECKS = [
    ('L-0485CB21', 'Stacks',
     lambda ctx: dict(usage=len(stacks(ctx)), source='cloudformation:ListStacks',
                      method='ACCOUNT_COUNT')),
    ('L-EC62D81A', 'Stack sets per administrator account',
     lambda ctx: dict(usage=len(stack_sets(ctx)), source='cloudformation:ListStackSets', method='ACCOUNT_COUNT')),
    ('L-DCC58E6D', 'Module limit per account',
     lambda ctx: dict(usage=len(types(ctx, 'MODULE')), source='cloudformation:ListTypes(MODULE)', method='ACCOUNT_COUNT')),
    ('L-24E9F9ED', 'Hooks per account',
     lambda ctx: dict(usage=len(types(ctx, 'HOOK')), source='cloudformation:ListTypes(HOOK)', method='ACCOUNT_COUNT')),
    ('L-C8225BA5', 'Stack instances per stack set', stack_instances_per_set),
]

EXTENDED_CHECKS = [
    ('L-9DE8E4FB', 'Private resource types per account',
     lambda ctx: dict(usage=len(types(ctx, 'RESOURCE')), source='cloudformation:ListTypes(RESOURCE)',
                      method='ACCOUNT_COUNT')),
    ('L-EA1018E8', 'Versions per private resource type', partial(versions_per_type, type_name='RESOURCE')),
    ('L-7E146E2E', 'Versions per module type', partial(versions_per_type, type_name='MODULE')),
    ('L-091DF7D9', 'Versions per hook', partial(versions_per_type, type_name='HOOK')),
    ('L-05BC894F', 'Template resources', partial(template_measure, measure='resources')),
    ('L-72B9A393', 'Template parameters', partial(template_measure, measure='parameters')),
    ('L-87D14FB7', 'Template outputs', partial(template_measure, measure='outputs')),
    ('L-63D096B8', 'Template mappings', partial(template_measure, measure='mappings')),
    ('L-1FFB6C73', 'Template mapping attributes', partial(template_measure, measure='mapping_attributes')),
    ('L-D663BAB9', 'Template dynamic references', partial(template_measure, measure='dynamic_references')),
    ('L-84B50260', 'Template logical resource ID length', partial(template_measure, measure='resource_name_length')),
    ('L-722F1E58', 'Template mapping and attribute name length', partial(template_measure, measure='mapping_name_length')),
    ('L-3B2D14A7', 'Template parameter name length', partial(template_measure, measure='parameter_name_length')),
    ('L-38FD7965', 'Template output name length', partial(template_measure, measure='output_name_length')),
    ('L-7C7532D4', 'Template description length', partial(template_measure, measure='description_length')),
    ('L-125EDA8C', 'Template size', partial(template_measure, measure='template_size')),
    ('L-255FC6A0', 'Maximum dependencies per stack set', dependencies_per_stack_set),
    ('L-AC58B440', 'Queued operations per stack set', queued_operations_per_stack_set),
]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_cloudformation(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cloudformation' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS if ('cloudformation', check[0]) in context.quotas]
    return context.run('cloudformation', checks, skip)
