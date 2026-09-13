"""AWS CodePipeline regional pipeline inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-78D200AD', 'Total pipelines',
           lambda ctx: dict(usage=len(ctx.call('codepipeline', 'list_pipelines', 'pipelines')),
                            source='codepipeline:ListPipelines', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_codepipeline(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codepipeline' for service, _ in context.quotas): return []
    return context.run('codepipeline', CHECKS, skip)
