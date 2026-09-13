"""Application Auto Scaling scalable-target inventories by namespace."""
from modules.qmcore.aws import CheckContext, session_from_env


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


def scalable_targets(ctx, namespace):
    return dict(usage=len(ctx.call('application-autoscaling', 'describe_scalable_targets',
                                   'ScalableTargets', ServiceNamespace=namespace)),
                source=f'application-autoscaling:DescribeScalableTargets({namespace})',
                method='ACCOUNT_COUNT')


CHECKS = [(code, f'Scalable targets for {name}',
           lambda ctx, ns=namespace: scalable_targets(ctx, ns))
          for code, (namespace, name) in TARGETS.items()]


def get_current_quotastatus_application_autoscaling(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'application-autoscaling' for service, _ in context.quotas):
        return []
    return context.run('application-autoscaling', CHECKS, skip)
