"""Model-scoped Bedrock batch job quotas, with explicit identity resolution."""
from functools import partial

from modules.qmcore.aws import NoData

# Reviewed against AWS batch-inference-supported.html on 2026-09-11.
# Quota codes below are fixed mappings, not inferred from names at runtime.
MODEL_QUOTAS = [
    ('L-E455959C', 'anthropic.claude-3-7-sonnet-20250219-v1:0', 'base'),
    ('L-A0AAB785', 'meta.llama3-1-405b-instruct-v1:0', 'base'),
    ('L-059C1AAB', 'meta.llama3-2-3b-instruct-v1:0', 'base'),
    ('L-E453CCF3', 'zai.glm-4.7-flash', 'base'),
    ('L-652C224A', 'amazon.titan-embed-image-v1', 'custom'),
    ('L-E2ED42E6', 'amazon.nova-lite-v1:0', 'base'),
    ('L-A986092E', 'mistral.mistral-small-2402-v1:0', 'base'),
    ('L-1AC1CABC', 'amazon.titan-embed-text-v2:0', 'base'),
    ('L-329D7443', 'amazon.titan-embed-text-v2:0', 'custom'),
    ('L-91E3DBE2', 'qwen.qwen3-235b-a22b-2507-v1:0', 'base'),
    ('L-1570CF9E', 'anthropic.claude-3-haiku-20240307-v1:0', 'base'),
    ('L-FE130012', 'amazon.nova-pro-v1:0', 'base'),
    ('L-10F69CA1', 'amazon.nova-2-lite-v1:0', 'base'),
    ('L-9A0F509C', 'anthropic.claude-3-opus-20240229-v1:0', 'base'),
    ('L-50CC95A8', 'openai.gpt-oss-20b-1:0', 'base'),
    ('L-95CB8E2F', 'mistral.devstral-2-123b', 'base'),
    ('L-C05EB25B', 'minimax.minimax-m2.1', 'base'),
    ('L-564C017C', 'amazon.nova-micro-v1:0', 'base'),
    ('L-3030E098', 'anthropic.claude-sonnet-4-6', 'base'),
    ('L-F30EAB98', 'qwen.qwen3-coder-30b-a3b-v1:0', 'base'),
    ('L-E83AC604', 'anthropic.claude-opus-4-5-20251101-v1:0', 'base'),
    ('L-7F2C6F33', 'amazon.titan-embed-image-v1', 'base'),
    ('L-5D367E5C', 'mistral.mistral-large-2407-v1:0', 'base'),
    ('L-79EFF176', 'anthropic.claude-sonnet-4-20250514-v1:0', 'base'),
    ('L-391478D2', 'meta.llama3-1-8b-instruct-v1:0', 'base'),
    ('L-FE24F76E', 'meta.llama3-3-70b-instruct-v1:0', 'base'),
    ('L-B0F56DCF', 'anthropic.claude-opus-4-6-v1', 'base'),
    ('L-8CC57EDA', 'meta.llama3-2-1b-instruct-v1:0', 'base'),
    ('L-07844084', 'openai.gpt-oss-120b-1:0', 'base'),
    ('L-62E2A345', 'meta.llama3-1-70b-instruct-v1:0', 'base'),
    ('L-220B8A25', 'anthropic.claude-3-5-haiku-20241022-v1:0', 'base'),
    ('L-63020993', 'anthropic.claude-haiku-4-5-20251001-v1:0', 'base'),
    ('L-7B9A79C8', 'qwen.qwen3-32b-v1:0', 'base'),
    ('L-A0300844', 'anthropic.claude-sonnet-4-5-20250929-v1:0', 'base'),
    ('L-3CCB3548', 'meta.llama3-2-11b-instruct-v1:0', 'base'),
    ('L-89923E2C', 'meta.llama3-2-90b-instruct-v1:0', 'base'),
    # The two catalog exports issue a second code for the same model under the
    # same display name. Adding the twin identifies no new model.
    ('L-5C48945B', 'qwen.qwen3-235b-a22b-2507-v1:0', 'base'),
    ('L-87CD099E', 'qwen.qwen3-32b-v1:0', 'base'),
    ('L-FEA282F8', 'qwen.qwen3-coder-30b-a3b-v1:0', 'base'),
]
TERMINAL = {'Completed', 'PartiallyCompleted', 'Failed', 'Stopped', 'Expired'}
COUNTED = {'Submitted', 'InProgress'}
# AWS exposes these states, but their precise quota-reservation semantics are
# not specified. Never quietly exclude a potentially reserved job.
TRANSITIONAL = {'Validating', 'Scheduled', 'Stopping'}
FOUNDATION_IDS = {model for _, model, _ in MODEL_QUOTAS}


def foundation_id(arn):
    parts = arn.split(':', 5)
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != 'bedrock'
            or parts[4] or not parts[5].startswith('foundation-model/')):
        raise NoData('Batch job base model is not a foundation-model ARN')
    model = parts[5].split('/', 1)[1]
    if not model or '/' in model:
        raise NoData('Batch job base model ARN is incomplete')
    return model


def resolve_model(ctx, identifier):
    if not isinstance(identifier, str) or not identifier:
        raise NoData('Batch job has no model identity')
    if identifier in FOUNDATION_IDS:
        return 'base', identifier
    if identifier.startswith('arn:'):
        parts = identifier.split(':', 5)
        if len(parts) != 6 or parts[2] != 'bedrock':
            raise NoData('Batch job has an invalid model ARN')
        resource = parts[5]
        if resource.startswith('foundation-model/'):
            return 'base', foundation_id(identifier)
        if resource.startswith('custom-model/'):
            custom = ctx.call('bedrock', 'get_custom_model', modelIdentifier=identifier)
            if custom.get('modelArn') != identifier:
                raise NoData('Batch custom model identity does not match the requested ARN')
            return 'custom', foundation_id(custom.get('baseModelArn') or '')
        profile = resource.startswith(('inference-profile/', 'application-inference-profile/'))
    else:
        profile = identifier.startswith(('us.', 'eu.', 'apac.', 'global.')) or '.' not in identifier
    if profile:
        result = ctx.call('bedrock', 'get_inference_profile', inferenceProfileIdentifier=identifier)
        if identifier not in {result.get('inferenceProfileId'), result.get('inferenceProfileArn')}:
            raise NoData('Batch inference profile identity does not match the requested identifier')
        models = {foundation_id(model.get('modelArn') or '') for model in result.get('models', [])}
        if len(models) != 1:
            raise NoData('Batch inference profile does not resolve to one foundation model')
        return 'base', models.pop()
    if not identifier.startswith('arn:'):
        # Establish the identity of other foundation models through AWS before
        # excluding them from a particular quota. Do not guess from a prefix.
        details = ctx.call('bedrock', 'get_foundation_model', modelIdentifier=identifier).get('modelDetails') or {}
        if details.get('modelId') == identifier:
            return 'base', identifier
    raise NoData('Batch job model identity has no verified resolution')


def batch_jobs(ctx, model, kind):
    usage, identities = 0, {}
    for job in ctx.call('bedrock', 'list_model_invocation_jobs', 'invocationJobSummaries'):
        arn, status = job.get('jobArn'), job.get('status')
        if not arn:
            raise NoData('Batch inventory has a job without its ARN')
        identity = (job.get('modelId'), status)
        if arn in identities:
            if identities[arn] != identity:
                raise NoData('Batch job changed during pagination')
            continue
        identities[arn] = identity
        if status in TERMINAL:
            continue
        if status not in COUNTED | TRANSITIONAL:
            raise NoData('Batch job has an unknown state')
        resolved_kind, resolved_model = resolve_model(ctx, job.get('modelId'))
        if (resolved_kind, resolved_model) != (kind, model):
            continue
        if status in TRANSITIONAL:
            raise NoData(f'Batch job quota reservation is unknown in state {status}')
        usage += 1
    return dict(usage=usage, source='bedrock:ListModelInvocationJobs+model-resolution',
                method='ACCOUNT_COUNT', meta={'foundationModelId': model, 'modelKind': kind})


CHECKS = [(code, f'Concurrent batch jobs using {kind} model {model}',
           partial(batch_jobs, model=model, kind=kind)) for code, model, kind in MODEL_QUOTAS]
