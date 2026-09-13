"""Amazon Polly regional lexicon quota."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-BC40090A', 'Lexicon count',
     lambda ctx: dict(usage=len(ctx.call('polly', 'list_lexicons', 'Lexicons')),
                      source='polly:ListLexicons', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_polly(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'polly' for service, _ in context.quotas):
        return []
    return context.run('polly', CHECKS, skip)
