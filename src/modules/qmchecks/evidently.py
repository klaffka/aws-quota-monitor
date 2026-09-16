"""CloudWatch Evidently regional project counts.

botocore no longer ships an `evidently` client; the call is still attempted so
the check recovers by itself if the SDK restores the service.
"""
from modules.qmcore.aws import CheckContext, sdk_call, session_from_env

EVIDENTLY = 'evidently'

CHECKS = [('L-B63A538F', 'Projects per AWS account',
           lambda ctx: dict(usage=len(sdk_call(ctx, EVIDENTLY, 'list_projects',
                                               'projects')),
                            source='evidently:ListProjects',
                            method='ACCOUNT_COUNT'))]


def get_current_quotastatus_evidently(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == EVIDENTLY for service, _ in context.quotas):
        return []
    return context.run(EVIDENTLY, CHECKS, skip)
