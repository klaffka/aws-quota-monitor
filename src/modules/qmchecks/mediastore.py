"""AWS Elemental MediaStore container inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-A05AAEF2', 'Containers',
           lambda ctx: dict(usage=len(ctx.call('mediastore', 'list_containers', 'Containers')),
                            source='mediastore:ListContainers', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_mediastore(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediastore' for service, _ in context.quotas): return []
    return context.run('mediastore', CHECKS, skip)
