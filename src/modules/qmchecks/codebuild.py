"""AWS CodeBuild project inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-ACCF6C0D', 'Build projects',
           lambda ctx: dict(usage=len(ctx.call('codebuild', 'list_projects', 'projects')),
                            source='codebuild:ListProjects', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_codebuild(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codebuild' for service, _ in context.quotas): return []
    return context.run('codebuild', CHECKS, skip)
