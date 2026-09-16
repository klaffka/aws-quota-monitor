"""AWS CodePipeline pipeline, stage, action and webhook quotas.

The timeout, artifact size and configuration length quotas bound a single
action or artifact. The `Minimum actions` and `Minimum stages per pipeline`
quotas state a floor rather than a ceiling, so a usage count means nothing
against them.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CODEPIPELINE = 'codepipeline'
EXECUTION_STATES = {'Cancelled', 'InProgress', 'Stopped', 'Stopping', 'Succeeded',
                    'Superseded', 'Failed'}
ACTIVE_STATES = {'InProgress', 'Stopping'}


def pipelines(ctx):
    found = []
    for pipeline in ctx.call(CODEPIPELINE, 'list_pipelines', 'pipelines'):
        name = pipeline.get('name')
        if not isinstance(name, str) or not name:
            raise NoData('CodePipeline pipeline is missing its name')
        if name not in found:
            found.append(name)
    return found


def stages(name, ctx):
    definition = ctx.call(CODEPIPELINE, 'get_pipeline', name=name).get('pipeline')
    if not isinstance(definition, dict):
        raise NoData('CodePipeline pipeline has no definition')
    found = definition.get('stages')
    if not isinstance(found, list) or not found:
        raise NoData('CodePipeline pipeline has no stages')
    for stage in found:
        if not isinstance(stage.get('actions'), list):
            raise NoData('CodePipeline stage has no actions')
    return found


def _run_orders(stage):
    counts = Counter()
    for action in stage['actions']:
        order = action.get('runOrder', 1)
        if not isinstance(order, int) or isinstance(order, bool) or order < 1:
            raise NoData('CodePipeline action has an invalid run order')
        counts[order] += 1
    return counts


def _pipeline_maximum(measure, source='codepipeline:GetPipeline'):
    def check(ctx):
        values = [(name, measure(stages(name, ctx)), None) for name in pipelines(ctx)]
        return maximum(values, 'CodePipeline', source)
    return check


def _stage_maximum(measure):
    def check(ctx):
        values = []
        for name in pipelines(ctx):
            for stage in stages(name, ctx):
                values.append((f"{name}/{stage.get('name')}", measure(stage), None))
        return maximum(values, 'CodePipelineStage', 'codepipeline:GetPipeline')
    return check


def active_executions_per_pipeline(ctx):
    values = []
    for name in pipelines(ctx):
        usage = 0
        for execution in ctx.call(CODEPIPELINE, 'list_pipeline_executions',
                                  'pipelineExecutionSummaries', pipelineName=name):
            status = execution.get('status')
            if status not in EXECUTION_STATES:
                raise NoData('CodePipeline execution has an unknown status')
            usage += status in ACTIVE_STATES
        values.append((name, usage, None))
    return maximum(values, 'CodePipeline', 'codepipeline:ListPipelineExecutions')


def custom_action_types(ctx):
    usage = 0
    for action in ctx.call(CODEPIPELINE, 'list_action_types', 'actionTypes'):
        identity = action.get('id')
        if not isinstance(identity, dict) or not identity.get('owner'):
            raise NoData('CodePipeline action type has no owner')
        usage += identity['owner'] == 'Custom'
    return dict(usage=usage, source='codepipeline:ListActionTypes',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-78D200AD', 'Total pipelines',
     lambda ctx: dict(usage=len(pipelines(ctx)), source='codepipeline:ListPipelines',
                      method='ACCOUNT_COUNT')),
    ('L-A0A99E23', 'Total stages per pipeline', _pipeline_maximum(len)),
    ('L-1402209C', 'Total actions per pipeline',
     _pipeline_maximum(lambda found: sum(len(stage['actions']) for stage in found))),
    ('L-570F1605', 'Total actions per stage',
     _stage_maximum(lambda stage: len(stage['actions']))),
    ('L-2B3011E2', 'Total parallel actions per stage',
     _stage_maximum(lambda stage: max(_run_orders(stage).values(), default=0))),
    ('L-8DF1BAAD', 'Total sequential actions per stage',
     _stage_maximum(lambda stage: len(_run_orders(stage)))),
    ('L-0097A9B4', 'Active executions per pipeline', active_executions_per_pipeline),
    ('L-519D5A90', 'Total custom actions', custom_action_types),
    ('L-FE939BB2', 'Total webhooks',
     lambda ctx: dict(usage=len(ctx.call(CODEPIPELINE, 'list_webhooks', 'webhooks')),
                      source='codepipeline:ListWebhooks', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_codepipeline(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codepipeline' for service, _ in context.quotas):
        return []
    return context.run('codepipeline', CHECKS, skip)
