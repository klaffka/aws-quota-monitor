"""CodeGuru Profiler profiling-group inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-DA8D4E8D', 'Number of profiling groups per account and region.',
     lambda c: dict(usage=len(c.call('codeguruprofiler', 'list_profiling_groups', 'profilingGroupNames')),
                    source='codeguruprofiler:ListProfilingGroups', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_codeguruprofiler(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codeguru-profiler' for service, _ in context.quotas):
        return []
    return context.run('codeguru-profiler', CHECKS, skip)
