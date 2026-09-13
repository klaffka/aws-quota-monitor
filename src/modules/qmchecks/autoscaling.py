"""Regional Auto Scaling inventory checks."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('autoscaling', method, key)),
                source=f'autoscaling:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-CDE20ADC', 'Auto Scaling groups per region',
     lambda ctx: resource_count(ctx, 'describe_auto_scaling_groups', 'AutoScalingGroups')),
    ('L-6B80B8FA', 'Launch configurations per region',
     lambda ctx: resource_count(ctx, 'describe_launch_configurations', 'LaunchConfigurations')),
]


def get_current_quotastatus_autoscaling(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'autoscaling' for service, _ in context.quotas):
        return []
    return context.run('autoscaling', CHECKS, skip)
