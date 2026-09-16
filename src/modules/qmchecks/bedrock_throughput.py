"""Provisioned throughput units and the concurrent jobs Bedrock runs.

Every quota here is reachable without resolving a model display name, which is
what blocks the per-model families in `bedrock_batch.py`.
"""
from modules.qmcore.aws import NoData, maximum

# A job that has not reached a terminal state still occupies its slot. Counting
# the complement rather than an allowlist means a state AWS adds later is
# counted rather than silently dropped.
INGESTION_FINISHED = {'COMPLETE', 'FAILED', 'STOPPED'}
BUILD_FINISHED = {'COMPLETED', 'FAILED', 'CANCELLED'}


def _model_kind(summary):
    """Say whether a provisioned throughput serves a base or a custom model."""
    arn = summary.get('modelArn')
    if not isinstance(arn, str) or ':' not in arn:
        raise NoData('Provisioned throughput has no model ARN')
    resource = arn.split(':', 5)[-1]
    if resource.startswith('foundation-model/'):
        return 'base'
    if resource.startswith('custom-model/'):
        return 'custom'
    raise NoData(f'Provisioned throughput model ARN is neither base nor custom: {resource}')


def no_commitment_units(ctx, kind):
    """Sum the model units of throughputs bought without a commitment term."""
    usage = 0
    for summary in ctx.call('bedrock', 'list_provisioned_model_throughputs',
                            'provisionedModelSummaries'):
        if summary.get('commitmentDuration'):
            continue
        if _model_kind(summary) != kind:
            continue
        units = summary.get('modelUnits')
        if not isinstance(units, int):
            raise NoData('Provisioned throughput reports no model units')
        usage += units
    return dict(usage=usage, source='bedrock:ListProvisionedModelThroughputs',
                method='ACCOUNT_SUM', meta={'modelKind': kind})


def _ingestion_jobs(ctx):
    """Yield (knowledge base, data source, unfinished job count) triples."""
    for base in ctx.call('bedrock-agent', 'list_knowledge_bases', 'knowledgeBaseSummaries'):
        base_id = base.get('knowledgeBaseId')
        if not base_id:
            raise NoData('Knowledge base inventory has an entry without its id')
        for source in ctx.call('bedrock-agent', 'list_data_sources', 'dataSourceSummaries',
                               knowledgeBaseId=base_id):
            source_id = source.get('dataSourceId')
            if not source_id:
                raise NoData('Data source inventory has an entry without its id')
            jobs = ctx.call('bedrock-agent', 'list_ingestion_jobs', 'ingestionJobSummaries',
                            knowledgeBaseId=base_id, dataSourceId=source_id)
            running = 0
            for job in jobs:
                status = job.get('status')
                if not status:
                    raise NoData('Ingestion job has no status')
                running += status not in INGESTION_FINISHED
            yield base_id, source_id, running


SOURCE_INGESTION = ('bedrock-agent:ListKnowledgeBases+ListDataSources+ListIngestionJobs')


def ingestion_jobs_per_account(ctx):
    return dict(usage=sum(running for _base, _source, running in _ingestion_jobs(ctx)),
                source=SOURCE_INGESTION, method='ACCOUNT_SUM')


def ingestion_jobs_per_knowledge_base(ctx):
    totals = {}
    for base_id, _source, running in _ingestion_jobs(ctx):
        totals[base_id] = totals.get(base_id, 0) + running
    return maximum([(base, running, None) for base, running in totals.items()],
                   'KnowledgeBase', SOURCE_INGESTION)


def ingestion_jobs_per_data_source(ctx):
    return maximum([(f'{base}/{source}', running, None)
                    for base, source, running in _ingestion_jobs(ctx)],
                   'KnowledgeBaseDataSource', SOURCE_INGESTION)


def _policy_builds(ctx):
    """Yield (policy ARN, unfinished build count) for every reasoning policy."""
    for policy in ctx.call('bedrock', 'list_automated_reasoning_policies',
                           'automatedReasoningPolicySummaries'):
        arn = policy.get('policyArn')
        if not arn:
            raise NoData('Automated Reasoning policy inventory has an entry without its ARN')
        workflows = ctx.call('bedrock', 'list_automated_reasoning_policy_build_workflows',
                             'automatedReasoningPolicyBuildWorkflowSummaries', policyArn=arn)
        yield arn, sum(workflow['status'] not in BUILD_FINISHED for workflow in workflows)


SOURCE_BUILDS = ('bedrock:ListAutomatedReasoningPolicies'
                 '+ListAutomatedReasoningPolicyBuildWorkflows')


def policy_builds_per_account(ctx):
    return dict(usage=sum(running for _arn, running in _policy_builds(ctx)),
                source=SOURCE_BUILDS, method='ACCOUNT_SUM')


def builds_per_policy(ctx):
    return maximum([(arn, running, None) for arn, running in _policy_builds(ctx)],
                   'AutomatedReasoningPolicy', SOURCE_BUILDS)


CHECKS = [
    ('L-FE44174A', 'Model units no-commitment Provisioned Throughputs across base models',
     lambda ctx: no_commitment_units(ctx, 'base')),
    ('L-BE77399C', 'Model units no-commitment Provisioned Throughputs across custom models',
     lambda ctx: no_commitment_units(ctx, 'custom')),
    ('L-795A8608', '(Knowledge Bases) Concurrent ingestion jobs per account',
     ingestion_jobs_per_account),
    ('L-31BC8F89', '(Knowledge Bases) Concurrent ingestion jobs per knowledge base',
     ingestion_jobs_per_knowledge_base),
    # The renamed product reissued this quota; the walk behind it is identical.
    ('L-D74F6A4C', '(Managed Knowledge Bases) Concurrent ingestion jobs per knowledge base',
     ingestion_jobs_per_knowledge_base),
    ('L-D38407FA', '(Knowledge Bases) Concurrent ingestion jobs per data source',
     ingestion_jobs_per_data_source),
    ('L-1B9EB555', '(Automated Reasoning) Concurrent policy builds per account',
     policy_builds_per_account),
    ('L-908FAEE3', '(Automated Reasoning) Concurrent builds per policy', builds_per_policy),
]
