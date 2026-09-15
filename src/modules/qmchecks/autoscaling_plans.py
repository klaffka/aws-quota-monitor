"""AWS Auto Scaling scaling plan and instruction quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

PLANS = 'autoscaling-plans'


def scaling_plans(ctx):
    found = {}
    for plan in ctx.call(PLANS, 'describe_scaling_plans', 'ScalingPlans'):
        name = plan.get('ScalingPlanName')
        if not isinstance(name, str) or not name:
            raise NoData('Scaling plan is missing its name')
        instructions = plan.get('ScalingInstructions')
        if not isinstance(instructions, list):
            raise NoData('Scaling plan has no instructions')
        found[name] = plan
    return found


def instructions_per_plan(ctx):
    values = [(name, len(plan['ScalingInstructions']), None)
              for name, plan in scaling_plans(ctx).items()]
    return maximum(values, 'ScalingPlan', 'autoscaling-plans:DescribeScalingPlans')


def configurations_per_instruction(ctx):
    values = []
    for name, plan in scaling_plans(ctx).items():
        for instruction in plan['ScalingInstructions']:
            resource = instruction.get('ResourceId')
            if not isinstance(resource, str) or not resource:
                raise NoData('Scaling instruction names no resource')
            configurations = instruction.get('TargetTrackingConfigurations')
            if not isinstance(configurations, list):
                raise NoData('Scaling instruction has no target tracking configuration')
            values.append((f'{name}/{resource}', len(configurations), None))
    return maximum(values, 'ScalingInstruction',
                   'autoscaling-plans:DescribeScalingPlans')


CHECKS = [
    ('L-BD401546', 'Scaling plans',
     lambda ctx: dict(usage=len(scaling_plans(ctx)),
                      source='autoscaling-plans:DescribeScalingPlans',
                      method='ACCOUNT_COUNT')),
    ('L-7FAA513E', 'Scaling instructions per scaling plan', instructions_per_plan),
    ('L-6538FA5E', 'Target tracking configurations per scaling instruction',
     configurations_per_instruction),
]


def get_current_quotastatus_autoscaling_plans(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'autoscaling-plans' for service, _ in context.quotas):
        return []
    return context.run('autoscaling-plans', CHECKS, skip)
