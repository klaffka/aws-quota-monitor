"""AWS re:Post private-space counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-4A83A41F', 'Number of private re:Posts',
           lambda c: dict(usage=len(c.call('repostspace', 'list_spaces', 'spaces')),
                          source='repostspace:ListSpaces', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_repostspace(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'repostspace' for service, _ in context.quotas): return []
    return context.run('repostspace', CHECKS, skip)
