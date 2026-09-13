"""Amazon Textract adapter inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-C9EC1D79', 'Adapters per account',
           lambda ctx: dict(usage=len(ctx.call('textract', 'list_adapters', 'Adapters')),
                            source='textract:ListAdapters', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_textract(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'textract' for service, _ in context.quotas): return []
    return context.run('textract', CHECKS, skip)
