"""CloudWatch Logs regional log-group inventory."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def _per_log_group(ctx, method, key):
    values = []
    for group in ctx.call('logs', 'describe_log_groups', 'logGroups'):
        name = group.get('logGroupName')
        if name:
            values.append((name, len(ctx.call('logs', method, key, logGroupName=name)), None))
    return maximum(values, 'LogGroup', f'logs:{method}')


CHECKS = [('L-C7B9AAAB', 'Log groups',
           lambda ctx: dict(usage=len(ctx.call('logs', 'describe_log_groups', 'logGroups')),
                            source='logs:DescribeLogGroups', method='ACCOUNT_COUNT')),
           ('L-89892494', 'Resource policies',
            lambda ctx: dict(usage=len(ctx.call('logs', 'describe_resource_policies', 'resourcePolicies')),
                             source='logs:DescribeResourcePolicies', method='ACCOUNT_COUNT')),
           ('L-87E7D306', 'Subscription filters per log group',
            lambda ctx: _per_log_group(ctx, 'describe_subscription_filters', 'subscriptionFilters')),
           ('L-3D5753EA', 'Metric filters per log group',
            lambda ctx: _per_log_group(ctx, 'describe_metric_filters', 'metricFilters'))]
CHECKS += [('L-B53B9649', 'Log anomaly detectors',
            lambda ctx: dict(usage=len(ctx.call('logs', 'list_log_anomaly_detectors', 'anomalyDetectors')),
                             source='logs:ListLogAnomalyDetectors', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_logs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'logs' for service, _ in context.quotas): return []
    return context.run('logs', CHECKS, skip)
