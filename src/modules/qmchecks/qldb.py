"""Amazon QLDB ledger inventory.

botocore no longer ships a `qldb` client; the call is still attempted so the
check recovers by itself if the SDK restores the service.
"""
from modules.qmcore.aws import CheckContext, sdk_call, session_from_env

QLDB = 'qldb'

CHECKS = [('L-CD70CADB', 'Ledgers',
           lambda ctx: dict(usage=len(sdk_call(ctx, QLDB, 'list_ledgers', 'Ledgers')),
                            source='qldb:ListLedgers', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_qldb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == QLDB for service, _ in context.quotas):
        return []
    return context.run(QLDB, CHECKS, skip)
