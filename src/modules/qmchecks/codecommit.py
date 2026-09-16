"""AWS CodeCommit repository inventory."""
from modules.qmcore.aws import CheckContext, session_from_env

CODECOMMIT = 'codecommit'

CHECKS = [
    ('L-81790602', 'Allowed repositories',
     lambda ctx: dict(usage=len(ctx.call(CODECOMMIT, 'list_repositories',
                                         'repositories')),
                      source='codecommit:ListRepositories', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_codecommit(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codecommit' for service, _ in context.quotas):
        return []
    return context.run('codecommit', CHECKS, skip)
