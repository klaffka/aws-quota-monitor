"""AWS Batch regional queue and compute-environment quotas."""
from modules.qmcore.aws import NoData, CheckContext, maximum, session_from_env


def queues(ctx):
    return ctx.call('batch', 'describe_job_queues', 'jobQueues')


def environments(ctx):
    return ctx.call('batch', 'describe_compute_environments', 'computeEnvironments')


def _job_queues(ctx):
    for queue in ctx.call('batch', 'describe_job_queues', 'jobQueues'):
        name = queue.get('jobQueueName')
        if not isinstance(name, str) or not name:
            raise NoData('Batch job queue is missing its name')
        yield name, queue


def service_environments_per_queue(ctx):
    return maximum([(name, len(queue.get('serviceEnvironmentOrder') or ()), None)
                    for name, queue in _job_queues(ctx)],
                   'BatchJobQueue', 'batch:DescribeJobQueues')


def share_identifiers_per_queue(ctx):
    """The identifiers live in the scheduling policy a queue names, if any."""
    queues = {name: queue.get('schedulingPolicyArn') for name, queue in _job_queues(ctx)}
    wanted = sorted({arn for arn in queues.values() if arn})
    shares = {}
    if wanted:
        for policy in ctx.call('batch', 'describe_scheduling_policies',
                               'schedulingPolicies', arns=wanted):
            arn = policy.get('arn')
            if not isinstance(arn, str) or not arn:
                raise NoData('Batch scheduling policy is missing its ARN')
            fairshare = policy.get('fairsharePolicy') or {}
            shares[arn] = len(fairshare.get('shareDistribution') or ())
    return maximum([(name, shares.get(arn, 0), None) for name, arn in sorted(queues.items())],
                   'BatchJobQueue', 'batch:DescribeSchedulingPolicies')


CHECKS = [
    ('L-4CEA37AD', 'Job queue limit',
     lambda c: dict(usage=len(queues(c)), source='batch:DescribeJobQueues', method='ACCOUNT_COUNT')),
    ('L-144F0CA5', 'Compute environment limit',
     lambda c: dict(usage=len(environments(c)), source='batch:DescribeComputeEnvironments', method='ACCOUNT_COUNT')),
    ('L-F8102809', 'Compute environments per job queue limit.',
     lambda c: maximum([(q.get('jobQueueArn') or q.get('jobQueueName'),
                         len(q.get('computeEnvironmentOrder', [])), None)
                        for q in queues(c)], 'JobQueue', 'batch:DescribeJobQueues')),
    ('L-61E3E54E', 'Service environment',
     lambda ctx: dict(usage=len(ctx.call('batch', 'describe_service_environments',
                                         'serviceEnvironments')),
                      source='batch:DescribeServiceEnvironments', method='ACCOUNT_COUNT')),
    ('L-80D92D24', 'Service environments per job queue', service_environments_per_queue),
    ('L-C997A649', 'Share identifiers per job queue limit.', share_identifiers_per_queue),
]


def get_current_quotastatus_batch(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'batch' for service, _ in context.quotas):
        return []
    return context.run('batch', CHECKS, skip)
