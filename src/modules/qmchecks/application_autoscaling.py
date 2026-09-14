"""Application Auto Scaling target, action, and policy inventories."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


TARGETS = {
    'L-D75CA9D2': ('elasticmapreduce', 'EMR'),
    'L-782A3EE2': ('ecs', 'ECS'),
    'L-799ACCDF': ('cassandra', 'Amazon Keyspaces'),
    'L-4A11ECEB': ('custom-resource', 'Custom resources'),
    'L-A1D42901': ('dynamodb', 'DynamoDB'),
    'L-297D9EC9': ('ec2', 'EC2'),
    'L-17D5F681': ('comprehend', 'Comprehend'),
    'L-1AAF0700': ('sagemaker', 'SageMaker'),
    'L-A2AD6458': ('lambda', 'Lambda'),
    'L-800F6F7B': ('rds', 'RDS'),
    'L-1A11EB4B': ('kafka', 'Amazon MSK'),
    'L-8998F403': ('appstream', 'AppStream'),
    'L-60E4E5E2': ('elasticache', 'ElastiCache'),
}

SERVICE_NAMESPACES = (
    'ecs', 'elasticmapreduce', 'ec2', 'appstream', 'dynamodb', 'rds',
    'sagemaker', 'custom-resource', 'comprehend', 'lambda', 'cassandra',
    'kafka', 'elasticache', 'neptune', 'workspaces',
)


def scalable_targets(ctx, namespace):
    return dict(usage=len(ctx.call('application-autoscaling', 'describe_scalable_targets',
                                   'ScalableTargets', ServiceNamespace=namespace)),
                source=f'application-autoscaling:DescribeScalableTargets({namespace})',
                method='ACCOUNT_COUNT')


def _target(item, namespace):
    if not isinstance(item, dict) or item.get('ServiceNamespace') != namespace:
        raise NoData('Application Auto Scaling inventory has an inconsistent namespace')
    resource_id = item.get('ResourceId')
    dimension = item.get('ScalableDimension')
    if (not isinstance(resource_id, str) or not resource_id
            or not isinstance(dimension, str) or not dimension):
        raise NoData('Application Auto Scaling inventory is missing a target identity')
    return namespace, resource_id, dimension


def _inventory(ctx, method, key, identity_field):
    inventory = []
    identities = set()
    for namespace in SERVICE_NAMESPACES:
        for item in ctx.call('application-autoscaling', method, key,
                             ServiceNamespace=namespace):
            target = _target(item, namespace)
            identity = item.get(identity_field)
            if not isinstance(identity, str) or not identity:
                raise NoData(f'Application Auto Scaling {key} item is missing an identity')
            if identity in identities:
                raise NoData(f'Application Auto Scaling {key} inventory contains a duplicate')
            identities.add(identity)
            inventory.append((identity, target, item))
    return inventory


def _target_label(target):
    return '/'.join(target)


def scheduled_actions_per_target(ctx):
    actions = _inventory(ctx, 'describe_scheduled_actions', 'ScheduledActions',
                         'ScheduledActionARN')
    counts = Counter(target for _, target, _ in actions)
    return maximum(((_target_label(target), count, None)
                    for target, count in counts.items()),
                   'ApplicationAutoScalingTarget',
                   'application-autoscaling:DescribeScheduledActions')


def scaling_policies(ctx):
    return _inventory(ctx, 'describe_scaling_policies', 'ScalingPolicies', 'PolicyARN')


def scaling_policies_per_target(ctx):
    counts = Counter(target for _, target, _ in scaling_policies(ctx))
    return maximum(((_target_label(target), count, None)
                    for target, count in counts.items()),
                   'ApplicationAutoScalingTarget',
                   'application-autoscaling:DescribeScalingPolicies')


def step_adjustments_per_policy(ctx):
    values = []
    for policy_arn, _, policy in scaling_policies(ctx):
        policy_type = policy.get('PolicyType')
        if policy_type not in {'StepScaling', 'TargetTrackingScaling',
                               'PredictiveScaling'}:
            raise NoData('Application Auto Scaling policy has an unknown type')
        if policy_type != 'StepScaling':
            continue
        configuration = policy.get('StepScalingPolicyConfiguration')
        adjustments = (configuration.get('StepAdjustments')
                       if isinstance(configuration, dict) else None)
        if (not isinstance(adjustments, list)
                or any(not isinstance(item, dict) for item in adjustments)):
            raise NoData('Application Auto Scaling step policy has invalid adjustments')
        values.append((policy_arn, len(adjustments), None))
    return maximum(values, 'ApplicationAutoScalingPolicy',
                   'application-autoscaling:DescribeScalingPolicies')


CHECKS = [(code, f'Scalable targets for {name}',
           lambda ctx, ns=namespace: scalable_targets(ctx, ns))
          for code, (namespace, name) in TARGETS.items()]
CHECKS.extend([
    ('L-95848B5F', 'Scheduled actions per scalable target',
     scheduled_actions_per_target),
    ('L-9C25247C', 'Step adjustments per step scaling policy',
     step_adjustments_per_policy),
    ('L-B395C81B', 'Scaling policies per scalable target',
     scaling_policies_per_target),
])


def get_current_quotastatus_application_autoscaling(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'application-autoscaling' for service, _ in context.quotas):
        return []
    return context.run('application-autoscaling', CHECKS, skip)
