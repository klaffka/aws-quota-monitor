"""AWS Batch regional queue and compute-environment quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def queues(ctx):
    return ctx.call('batch', 'describe_job_queues', 'jobQueues')


def environments(ctx):
    return ctx.call('batch', 'describe_compute_environments', 'computeEnvironments')


CHECKS = [
    ('L-4CEA37AD', 'Job queue limit',
     lambda c: dict(usage=len(queues(c)), source='batch:DescribeJobQueues', method='ACCOUNT_COUNT')),
    ('L-144F0CA5', 'Compute environment limit',
     lambda c: dict(usage=len(environments(c)), source='batch:DescribeComputeEnvironments', method='ACCOUNT_COUNT')),
    ('L-F8102809', 'Compute environments per job queue limit.',
     lambda c: maximum([(q.get('jobQueueArn') or q.get('jobQueueName'),
                         len(q.get('computeEnvironmentOrder', [])), None)
                        for q in queues(c)], 'JobQueue', 'batch:DescribeJobQueues')),
]


def get_current_quotastatus_batch(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'batch' for service, _ in context.quotas):
        return []
    return context.run('batch', CHECKS, skip)
