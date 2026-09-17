"""Advanced Prompt Optimization job counts.

Bedrock bounds these jobs twice: how many may run at once, and how many
finished ones may be kept. The listing has no status filter, so both counts
come from one walk of the same inventory.
"""
from modules.qmcore.aws import NoData


# Listed by the API itself, so an unknown value means the service grew a state
# this split has not been reviewed against.
RUNNING = {'InProgress', 'Stopping'}
FINISHED = {'Completed', 'Failed', 'PartiallyCompleted', 'Stopped', 'Deleting'}
SOURCE = 'bedrock:ListAdvancedPromptOptimizationJobs'


def _jobs(ctx, wanted):
    usage = 0
    for job in ctx.call('bedrock', 'list_advanced_prompt_optimization_jobs', 'jobSummaries'):
        status = job.get('jobStatus')
        if status not in RUNNING | FINISHED:
            raise NoData('Advanced Prompt Optimization job has an unknown status')
        usage += status in wanted
    return dict(usage=usage, source=SOURCE, method='ACCOUNT_COUNT')


def active_jobs(ctx):
    return _jobs(ctx, RUNNING)


def inactive_jobs(ctx):
    return _jobs(ctx, FINISHED)


# Both catalog exports name these quotas, each under its own code.
CHECKS = [
    ('L-7380B9B2', '(Advanced Prompt Optimization) Active jobs per account', active_jobs),
    ('L-B46DD052', '(Advanced Prompt Optimization) Active jobs per account', active_jobs),
    ('L-0B66D421', '(Advanced Prompt Optimization) Inactive jobs per account', inactive_jobs),
    ('L-986C4672', '(Advanced Prompt Optimization) Inactive jobs per account', inactive_jobs),
]
