"""AWS Step Functions resource quotas backed by complete inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('stepfunctions', method, key)),
                source=f'stepfunctions:{method}', method='ACCOUNT_COUNT')


def versions_per_state_machine(ctx):
    values = []
    for machine in ctx.call('stepfunctions', 'list_state_machines', 'stateMachines'):
        arn = machine.get('stateMachineArn')
        if arn:
            values.append((arn, len(ctx.call('stepfunctions', 'list_state_machine_versions',
                                             'stateMachineVersions', stateMachineArn=arn)), None))
    return maximum(values, 'StateMachine', 'stepfunctions:ListStateMachines+ListStateMachineVersions')


def aliases_per_state_machine(ctx):
    values = []
    for machine in ctx.call('stepfunctions', 'list_state_machines', 'stateMachines'):
        arn = machine.get('stateMachineArn')
        if arn:
            values.append((arn, len(ctx.call('stepfunctions', 'list_state_machine_aliases',
                                             'stateMachineAliases', stateMachineArn=arn)), None))
    return maximum(values, 'StateMachine', 'stepfunctions:ListStateMachines+ListStateMachineAliases')


CHECKS = [
    ('L-B66B0F91', 'Registered state machines',
     lambda ctx: resource_count(ctx, 'list_state_machines', 'stateMachines')),
    ('L-A9562A73', 'Registered activities',
     lambda ctx: resource_count(ctx, 'list_activities', 'activities')),
    ('L-6AFCB355', 'Published state machine versions per state machine', versions_per_state_machine),
    ('L-C1D5EBBB', 'State machine aliases per state machine', aliases_per_state_machine),
]


def get_current_quotastatus_stepfunctions(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    # Service Quotas is not enabled in every region. Do not manufacture
    # unsupported measurements by probing a service absent from the catalog.
    if not any(service == 'states' for service, _ in context.quotas):
        return []
    return context.run('states', CHECKS, skip)
