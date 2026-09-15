"""AWS Security Agent concurrent job quotas, counted across agent spaces."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

AGENT = 'securityagent'
JOB_STATES = {'IN_PROGRESS', 'STOPPING', 'STOPPED', 'FAILED', 'COMPLETED'}
RUNNING_STATES = {'IN_PROGRESS', 'STOPPING'}


def agent_spaces(ctx):
    found = set()
    for space in ctx.call(AGENT, 'list_agent_spaces', 'agentSpaceSummaries'):
        identity = space.get('agentSpaceId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Security agent space is missing its identity')
        found.add(identity)
    return sorted(found)


def _running_jobs(parent_method, parent_key, parent_field,
                  job_method, job_key, job_argument, subject):
    """Walk each agent space's work items and count the jobs still running."""
    def check(ctx):
        usage = 0
        for space in agent_spaces(ctx):
            for parent in ctx.call(AGENT, parent_method, parent_key,
                                   agentSpaceId=space):
                identity = parent.get(parent_field)
                if not isinstance(identity, str) or not identity:
                    raise NoData(f'Security agent {subject} is missing its identity')
                for job in ctx.call(AGENT, job_method, job_key, agentSpaceId=space,
                                    **{job_argument: identity}):
                    status = job.get('status')
                    if status not in JOB_STATES:
                        raise NoData(f'Security agent {subject} job has an '
                                     'unknown status')
                    usage += status in RUNNING_STATES
        operation = ''.join(part.capitalize() for part in job_method.split('_'))
        return dict(usage=usage, source=f'securityagent:{operation}',
                    method='ACCOUNT_COUNT')
    return check


CHECKS = [
    ('L-EC8BA326', 'Concurrently Running Code Review Jobs',
     _running_jobs('list_code_reviews', 'codeReviewSummaries', 'codeReviewId',
                   'list_code_review_jobs_for_code_review', 'codeReviewJobSummaries',
                   'codeReviewId', 'code review')),
    ('L-5EB2D333', 'Concurrently Running Pentest Jobs',
     _running_jobs('list_pentests', 'pentestSummaries', 'pentestId',
                   'list_pentest_jobs_for_pentest', 'pentestJobSummaries',
                   'pentestId', 'pentest')),
    ('L-812A42D7', 'Concurrently Running Threat Model Jobs',
     _running_jobs('list_threat_models', 'threatModelSummaries', 'threatModelId',
                   'list_threat_model_jobs', 'threatModelJobSummaries',
                   'threatModelId', 'threat model')),
]


def get_current_quotastatus_securityagent(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'securityagent' for service, _ in context.quotas):
        return []
    return context.run('securityagent', CHECKS, skip)
