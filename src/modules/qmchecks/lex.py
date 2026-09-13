"""Amazon Lex V2 regional bot resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def bots(ctx):
    return ctx.call('lexv2-models', 'list_bots', 'botSummaries')


def versions_per_bot(ctx):
    values = []
    for bot in bots(ctx):
        bot_id = bot.get('botId')
        versions = ctx.call('lexv2-models', 'list_bot_versions', 'botVersionSummaries', botId=bot_id)
        values.append((bot_id, len(versions), None))
    return maximum(values, 'LexBot', 'lexv2-models:ListBotVersions')


CHECKS = [
    ('L-36FA8BD2', 'Bots per account',
     lambda ctx: dict(usage=len(bots(ctx)), source='lexv2-models:ListBots', method='ACCOUNT_COUNT')),
    ('L-BCD96794', 'Versions per bot', versions_per_bot),
]


def get_current_quotastatus_lex(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'lex' for service, _ in context.quotas):
        return []
    return context.run('lex', CHECKS, skip)
