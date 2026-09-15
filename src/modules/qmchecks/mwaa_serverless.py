"""Amazon MWAA Serverless workflow, version and run quotas.

Code storage, workflow definition size, task execution timeout and XCom data
size bound a single artifact or task rather than an inventory.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

MWAA = 'mwaa-serverless'
RUN_STATES = {'STARTING', 'QUEUED', 'RUNNING', 'SUCCESS', 'FAILED', 'TIMEOUT',
              'STOPPING', 'STOPPED'}
RUNNING_STATES = {'STARTING', 'QUEUED', 'RUNNING', 'STOPPING'}


def workflows(ctx):
    found = {}
    for workflow in ctx.call(MWAA, 'list_workflows', 'Workflows'):
        arn = workflow.get('WorkflowArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Serverless workflow is missing its ARN')
        found[arn] = workflow.get('Name') or arn
    return found


def versions_per_workflow(ctx):
    values = []
    for arn, name in workflows(ctx).items():
        versions = ctx.call(MWAA, 'list_workflow_versions', 'WorkflowVersions',
                            WorkflowArn=arn)
        for version in versions:
            if not isinstance(version.get('WorkflowVersion'), str):
                raise NoData('Serverless workflow version has no version')
        values.append((name, len(versions), None))
    return maximum(values, 'ServerlessWorkflow', 'mwaa-serverless:ListWorkflowVersions')


def concurrent_runs(ctx):
    usage = 0
    for arn in workflows(ctx):
        for run in ctx.call(MWAA, 'list_workflow_runs', 'WorkflowRuns',
                            WorkflowArn=arn):
            detail = run.get('RunDetailSummary')
            if not isinstance(detail, dict):
                raise NoData('Serverless workflow run has no detail')
            status = detail.get('Status')
            if status not in RUN_STATES:
                raise NoData('Serverless workflow run has an unknown status')
            usage += status in RUNNING_STATES
    return dict(usage=usage, source='mwaa-serverless:ListWorkflowRuns',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-D905802C', 'Maximum workflows per account',
     lambda ctx: dict(usage=len(workflows(ctx)),
                      source='mwaa-serverless:ListWorkflows', method='ACCOUNT_COUNT')),
    ('L-430BC7B5', 'Maximum workflow versions per workflow', versions_per_workflow),
    ('L-643FB251', 'Maximum concurrent workflow runs per account', concurrent_runs),
]


def get_current_quotastatus_airflow_serverless(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'airflow-serverless' for service, _ in context.quotas):
        return []
    return context.run('airflow-serverless', CHECKS, skip)
