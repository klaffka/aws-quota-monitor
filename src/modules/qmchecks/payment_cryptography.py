"""AWS Payment Cryptography regional key counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-23280857', 'Keys',
     lambda c: dict(usage=len(c.call('payment-cryptography', 'list_keys', 'Keys')),
                    source='payment-cryptography:ListKeys', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_payment_cryptography(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'payment-cryptography' for service, _ in context.quotas):
        return []
    return context.run('payment-cryptography', CHECKS, skip)
