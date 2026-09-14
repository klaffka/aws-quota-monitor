"""CloudWatch Evidently regional project counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-B63A538F', 'Projects per AWS account',
           lambda c: dict(usage=len(c.call('evidently', 'list_projects', 'projects')),
                          source='evidently:ListProjects', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_evidently(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'evidently' for service, _ in context.quotas): return []
    return context.run('evidently', CHECKS, skip)
