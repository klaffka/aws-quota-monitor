"""AWS Payment Cryptography regional key and alias counts."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env


def alias_count(ctx):
    aliases = {}
    for item in ctx.call('payment-cryptography', 'list_aliases', 'Aliases'):
        if not isinstance(item, dict):
            raise NoData('Payment Cryptography alias inventory contains an invalid item')
        name = item.get('AliasName')
        key_arn = item.get('KeyArn')
        if not isinstance(name, str) or not name.startswith('alias/') or len(name) <= 6:
            raise NoData('Payment Cryptography alias has an invalid name')
        if key_arn is not None:
            parts = key_arn.split(':', 5) if isinstance(key_arn, str) else []
            if (len(parts) != 6 or parts[0] != 'arn'
                    or parts[2] != 'payment-cryptography'
                    or parts[3] != ctx.region or parts[4] != ctx.account
                    or not parts[5].startswith('key/') or len(parts[5]) <= 4):
                raise NoData('Payment Cryptography alias has an inconsistent key ARN')
        if name in aliases:
            if aliases[name] != item:
                raise NoData('Payment Cryptography alias changed during pagination')
            continue
        aliases[name] = item
    return dict(usage=len(aliases), source='payment-cryptography:ListAliases',
                method='ACCOUNT_COUNT')

CHECKS = [
    ('L-23280857', 'Keys',
     lambda c: dict(usage=len(c.call('payment-cryptography', 'list_keys', 'Keys')),
                    source='payment-cryptography:ListKeys', method='ACCOUNT_COUNT')),
    ('L-10DEBB19', 'Aliases', alias_count),
]


def get_current_quotastatus_payment_cryptography(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'payment-cryptography' for service, _ in context.quotas):
        return []
    return context.run('payment-cryptography', CHECKS, skip)
