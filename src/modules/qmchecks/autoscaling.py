"""Regional Auto Scaling inventory and per-group scope checks.

Policies, scheduled actions and notifications are listed for the whole account
and name the group they belong to, so the per-group maxima need no call per
group. Only the lifecycle hooks are listed per group.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SERVICE = 'autoscaling'


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call(SERVICE, method, key)),
                source=f'autoscaling:{method}', method='ACCOUNT_COUNT')


def groups(ctx):
    for entry in ctx.call(SERVICE, 'describe_auto_scaling_groups', 'AutoScalingGroups'):
        name = entry.get('AutoScalingGroupName')
        if not isinstance(name, str) or not name:
            raise NoData('Auto Scaling group is missing its name')
        yield name, entry


def attachments_per_group(ctx, member):
    """Both attachment lists travel with the group, so no detail call is made."""
    return maximum([(name, len(entry.get(member) or ()), None)
                    for name, entry in groups(ctx)],
                   'AutoScalingGroup', 'autoscaling:DescribeAutoScalingGroups')


def _by_group(ctx, method, key, value=None):
    """Count an account-wide listing against the group each entry names."""
    counts = {}
    for entry in ctx.call(SERVICE, method, key):
        name = entry.get('AutoScalingGroupName')
        if not isinstance(name, str) or not name:
            raise NoData(f'Auto Scaling {key} entry names no group')
        if value is None:
            counts[name] = counts.get(name, 0) + 1
        else:
            item = entry.get(value)
            if not isinstance(item, str) or not item:
                raise NoData(f'Auto Scaling {key} entry has no {value}')
            counts.setdefault(name, set()).add(item)
    return maximum([(name, count if value is None else len(count), None)
                    for name, count in sorted(counts.items())],
                   'AutoScalingGroup', f'autoscaling:{method}')


def step_adjustments_per_policy(ctx):
    """The quota bounds one policy's adjustments, not a group's policies."""
    values = []
    for policy in ctx.call(SERVICE, 'describe_policies', 'ScalingPolicies'):
        group = policy.get('AutoScalingGroupName')
        name = policy.get('PolicyName')
        if not group or not name:
            raise NoData('Auto Scaling policy is missing its group or its name')
        values.append((f'{group}/{name}', len(policy.get('StepAdjustments') or ()), None))
    return maximum(values, 'AutoScalingPolicy', 'autoscaling:DescribePolicies')


def lifecycle_hooks_per_group(ctx):
    return maximum([(name, len(ctx.call(SERVICE, 'describe_lifecycle_hooks', 'LifecycleHooks',
                                        AutoScalingGroupName=name)), None)
                    for name, _entry in groups(ctx)],
                   'AutoScalingGroup', 'autoscaling:DescribeLifecycleHooks')


CHECKS = [
    ('L-CDE20ADC', 'Auto Scaling groups per region',
     lambda ctx: resource_count(ctx, 'describe_auto_scaling_groups', 'AutoScalingGroups')),
    ('L-6B80B8FA', 'Launch configurations per region',
     lambda ctx: resource_count(ctx, 'describe_launch_configurations', 'LaunchConfigurations')),
    ('L-F786B2E5', 'Classic Load Balancers per Auto Scaling group',
     lambda ctx: attachments_per_group(ctx, 'LoadBalancerNames')),
    ('L-05CB8B12', 'Target groups per Auto Scaling group',
     lambda ctx: attachments_per_group(ctx, 'TargetGroupARNs')),
    ('L-72753F6F', 'Scaling policies per Auto Scaling group',
     lambda ctx: _by_group(ctx, 'describe_policies', 'ScalingPolicies')),
    ('L-F0B00D71', 'Scheduled actions per Auto Scaling group',
     lambda ctx: _by_group(ctx, 'describe_scheduled_actions', 'ScheduledUpdateGroupActions')),
    # A topic notified about several events is returned once per event type.
    ('L-CEE5E714', 'SNS topics per Auto Scaling group',
     lambda ctx: _by_group(ctx, 'describe_notification_configurations',
                           'NotificationConfigurations', value='TopicARN')),
    ('L-6C2A2F6E', 'Step adjustments per step scaling policy', step_adjustments_per_policy),
    ('L-1312BBBF', 'Lifecycle hooks per Auto Scaling group', lifecycle_hooks_per_group),
]


def get_current_quotastatus_autoscaling(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'autoscaling' for service, _ in context.quotas):
        return []
    return context.run('autoscaling', CHECKS, skip)
