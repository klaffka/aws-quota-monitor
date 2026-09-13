"""Recycle Bin regional rule counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-629917A2', 'Rules per Region', lambda c: dict(usage=len(c.call('rbin', 'list_rules', 'Rules')), source='rbin:ListRules', method='ACCOUNT_COUNT'))]

def get_current_quotastatus_rbin(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rbin' for service, _ in context.quotas): return []
    return context.run('rbin', CHECKS, skip)
