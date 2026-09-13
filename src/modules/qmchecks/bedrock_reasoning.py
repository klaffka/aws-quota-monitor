"""Automated Reasoning policy inventories and configuration maxima."""
import re
from functools import partial

from modules.qmcore.aws import NoData, maximum


POLICY_ARN = re.compile(
    r'(arn:aws(?:-[^:]+)?:bedrock:[a-z0-9-]+:[0-9]{12}:'
    r'automated-reasoning-policy/([a-z0-9]{12}))(?::([1-9][0-9]*))?')


def policy_identity(item):
    match = POLICY_ARN.fullmatch(item.get('policyArn', ''))
    if not match or item.get('policyId') != match[2]:
        raise NoData('Automated Reasoning policy identity is missing or inconsistent')
    version = item.get('version')
    # The API represents a working draft by its unversioned ARN. The SDK
    # permits an empty version string as well as the documented DRAFT label.
    if version in {'', 'DRAFT'} and match[3] is None:
        return match[1], 'DRAFT'
    if not isinstance(version, str) or not re.fullmatch(r'[1-9][0-9]*', version):
        raise NoData('Automated Reasoning policy has an unknown version')
    if match[3] is not None and version != match[3]:
        raise NoData('Automated Reasoning policy ARN and version disagree')
    return match[1], version


def policies(ctx):
    result = set()
    for item in ctx.call('bedrock', 'list_automated_reasoning_policies',
                         'automatedReasoningPolicySummaries'):
        arn, version = policy_identity(item)
        if version != 'DRAFT':
            raise NoData('Unfiltered policy inventory did not return working drafts')
        result.add(arn)
    return sorted(result)


def policy_versions(ctx, arn):
    result = set()
    for item in ctx.call('bedrock', 'list_automated_reasoning_policies',
                         'automatedReasoningPolicySummaries', policyArn=arn):
        parent, version = policy_identity(item)
        if parent != arn:
            raise NoData('Automated Reasoning version belongs to another policy')
        if version != 'DRAFT':
            result.add(version)
    return sorted(result, key=int)


def policy_definitions(ctx):
    for arn in policies(ctx):
        for version in ['DRAFT', *policy_versions(ctx, arn)]:
            target = arn if version == 'DRAFT' else f'{arn}:{version}'
            response = ctx.call('bedrock', 'export_automated_reasoning_policy_version', policyArn=target)
            definition = response.get('policyDefinition')
            if not isinstance(definition, dict):
                raise NoData('Automated Reasoning export has no policy definition')
            yield target, definition


def entries(definition, field, required=False):
    value = definition.get(field, None if required else [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise NoData('Automated Reasoning definition has an invalid configuration list')
    return value


def configuration(ctx, field, per_type=False):
    values = []
    for arn, definition in policy_definitions(ctx):
        items = entries(definition, field)
        if per_type:
            for index, item in enumerate(items):
                # Use a positional identifier: policy type names/content need
                # not be copied into measurement metadata.
                values.append((f'{arn}/type/{index}', len(entries(item, 'values', required=True)), None))
        else:
            values.append((arn, len(items), None))
    return maximum(values, 'AutomatedReasoningPolicyType' if per_type else 'AutomatedReasoningPolicyVersion',
                   'bedrock:ExportAutomatedReasoningPolicyVersion')


def version_count(ctx):
    return maximum([(arn, len(policy_versions(ctx, arn)), None) for arn in policies(ctx)],
                   'AutomatedReasoningPolicy', 'bedrock:ListAutomatedReasoningPolicies')


def test_count(ctx):
    values = []
    for arn in policies(ctx):
        ids = set()
        for item in ctx.call('bedrock', 'list_automated_reasoning_policy_test_cases', 'testCases', policyArn=arn):
            identity = item.get('testCaseId')
            if not isinstance(identity, str) or not identity:
                raise NoData('Automated Reasoning test case has no identity')
            ids.add(identity)
        values.append((arn, len(ids), None))
    return maximum(values, 'AutomatedReasoningPolicy', 'bedrock:ListAutomatedReasoningPolicyTestCases')


CHECKS = [
    ('L-F32E9946', 'Types per policy', partial(configuration, field='types')),
    ('L-07EE48DE', 'Variables in policy', partial(configuration, field='variables')),
    ('L-31B8EB64', 'Rules in policy', partial(configuration, field='rules')),
    ('L-C4A2EDC7', 'Values per type in policy', partial(configuration, field='types', per_type=True)),
    ('L-83504243', 'Versions per policy', version_count),
    ('L-54C7BE29', 'Tests per policy', test_count),
]
