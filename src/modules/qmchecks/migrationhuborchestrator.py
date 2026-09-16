"""AWS Migration Hub Orchestrator workflow, step group and step quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

ORCHESTRATOR = 'migrationhuborchestrator'


def workflows(ctx):
    found = set()
    for workflow in ctx.call(ORCHESTRATOR, 'list_workflows',
                             'migrationWorkflowSummary'):
        identity = workflow.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Migration workflow is missing its identity')
        found.add(identity)
    return sorted(found)


def step_groups(workflow, ctx):
    found = []
    for group in ctx.call(ORCHESTRATOR, 'list_workflow_step_groups',
                          'workflowStepGroupsSummary', workflowId=workflow):
        identity = group.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Migration step group is missing its identity')
        found.append(identity)
    return found


def step_groups_per_workflow(ctx):
    values = [(workflow, len(step_groups(workflow, ctx)), None)
              for workflow in workflows(ctx)]
    return maximum(values, 'MigrationWorkflow',
                   'migrationhuborchestrator:ListWorkflowStepGroups')


def steps_per_step_group(ctx):
    values = []
    for workflow in workflows(ctx):
        for group in step_groups(workflow, ctx):
            steps = ctx.call(ORCHESTRATOR, 'list_workflow_steps', 'workflowStepsSummary',
                             workflowId=workflow, stepGroupId=group)
            values.append((f'{workflow}/{group}', len(steps), None))
    return maximum(values, 'MigrationStepGroup',
                   'migrationhuborchestrator:ListWorkflowSteps')


CHECKS = [
    ('L-9E55B371', 'Maximum workflows',
     lambda ctx: dict(usage=len(workflows(ctx)),
                      source='migrationhuborchestrator:ListWorkflows',
                      method='ACCOUNT_COUNT')),
    ('L-FD489B05', 'Maximum step groups per workflow', step_groups_per_workflow),
    ('L-71F71C2E', 'Maximum steps per step group', steps_per_step_group),
]


def get_current_quotastatus_migrationhuborchestrator(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'migrationhuborchestrator' for service, _ in context.quotas):
        return []
    return context.run('migrationhuborchestrator', CHECKS, skip)
