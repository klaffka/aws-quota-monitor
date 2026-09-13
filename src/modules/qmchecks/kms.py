"""Regional AWS KMS resource quotas backed by paginated inventories."""
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.aws import maximum


def keys(ctx):
    return ctx.call('kms', 'list_keys', 'Keys')


def customer_keys(ctx):
    """Return only customer-managed keys covered by the CMK quota.

    ``ListKeys`` includes AWS-managed keys, which the 100,000 CMK quota
    explicitly excludes.  Describe each key to inspect ``KeyManager`` rather
    than silently over-counting service-managed keys.
    """
    result = []
    for key in keys(ctx):
        metadata = ctx.call('kms', 'describe_key', KeyId=key['KeyId'])['KeyMetadata']
        if metadata.get('KeyManager', 'CUSTOMER') == 'CUSTOMER':
            result.append(key)
    return result


CHECKS = [
    ('L-C2F1777E', 'Customer Master Keys (CMKs)',
     lambda ctx: dict(usage=len(customer_keys(ctx)), source='kms:ListKeys+DescribeKey', method='ACCOUNT_COUNT')),
    ('L-340F62FB', 'Aliases per CMK',
     lambda ctx: maximum([(key['KeyId'], len(ctx.call('kms', 'list_aliases', 'Aliases', KeyId=key['KeyId']),), None)
                          for key in customer_keys(ctx)], 'KMSKey', 'kms:ListAliases')),
    ('L-D594A657', 'Grants per CMK',
     lambda ctx: maximum([(key['KeyId'], len(ctx.call('kms', 'list_grants', 'Grants', KeyId=key['KeyId']),), None)
                          for key in customer_keys(ctx)], 'KMSKey', 'kms:ListGrants')),
    ('L-F33DCFEB', 'Custom Key Stores',
     lambda ctx: dict(usage=len(ctx.call('kms', 'list_custom_key_stores', 'CustomKeyStores')),
                      source='kms:ListCustomKeyStores', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_kms(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kms' for service, _ in context.quotas):
        return []
    return context.run('kms', CHECKS, skip)
