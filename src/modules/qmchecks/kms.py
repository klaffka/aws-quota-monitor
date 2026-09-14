"""Regional AWS KMS resource quotas backed by paginated inventories."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


KEY_MANAGERS = {'AWS', 'CUSTOMER'}
KEY_STATES = {
    'Creating', 'Enabled', 'Disabled', 'PendingDeletion', 'PendingImport',
    'PendingReplicaDeletion', 'Unavailable', 'Updating',
}
KEY_SPECS = {
    'SYMMETRIC_DEFAULT', 'RSA_2048', 'RSA_3072', 'RSA_4096',
    'ECC_NIST_P256', 'ECC_NIST_P384', 'ECC_NIST_P521',
    'ECC_SECG_P256K1', 'HMAC_224', 'HMAC_256', 'HMAC_384', 'HMAC_512',
    'SM2', 'ML_DSA_44', 'ML_DSA_65', 'ML_DSA_87',
    'ECC_NIST_EDWARDS25519',
}
KEY_USAGES = {'ENCRYPT_DECRYPT', 'SIGN_VERIFY', 'GENERATE_VERIFY_MAC',
              'KEY_AGREEMENT'}
KEY_ORIGINS = {'AWS_KMS', 'EXTERNAL', 'AWS_CLOUDHSM', 'EXTERNAL_KEY_STORE'}
ROTATION_TYPES = {'AUTOMATIC', 'ON_DEMAND'}
MATERIAL_STATES = {
    'CURRENT', 'NON_CURRENT', 'PENDING_ROTATION',
    'PENDING_MULTI_REGION_IMPORT_AND_ROTATION',
}
STORE_TYPES = {'AWS_CLOUDHSM', 'EXTERNAL_KEY_STORE'}
STORE_STATES = {'CONNECTED', 'CONNECTING', 'FAILED', 'DISCONNECTED',
                'DISCONNECTING'}


def _validate_arn(ctx, arn, resource, subject):
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or not parts[1].startswith('aws')
            or parts[2] != 'kms' or parts[3] != ctx.region
            or parts[4] != ctx.account or parts[5] != resource):
        raise NoData(f'KMS {subject} has an inconsistent ARN')


def _dedupe(items, identity, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'KMS {subject} inventory contains an invalid item')
        identifier = item.get(identity)
        if not isinstance(identifier, str) or not identifier:
            raise NoData(f'KMS {subject} is missing its identity')
        if identifier in result:
            if result[identifier] != item:
                raise NoData(f'KMS {subject} changed during pagination')
            continue
        result[identifier] = item
    return result


def keys(ctx):
    listed = _dedupe(ctx.call('kms', 'list_keys', 'Keys'), 'KeyId', 'key')
    result = {}
    for key_id, item in listed.items():
        arn = item.get('KeyArn')
        _validate_arn(ctx, arn, f'key/{key_id}', 'key')
        detail = ctx.call('kms', 'describe_key', KeyId=key_id)
        metadata = detail.get('KeyMetadata') if isinstance(detail, dict) else None
        if not isinstance(metadata, dict):
            raise NoData('KMS key is missing its metadata')
        if metadata.get('KeyId') != key_id or metadata.get('Arn') != arn:
            raise NoData('KMS key changed during collection')
        if metadata.get('KeyManager') not in KEY_MANAGERS:
            raise NoData('KMS key has an unknown manager')
        if metadata.get('KeyState') not in KEY_STATES:
            raise NoData('KMS key has an unknown state')
        if metadata.get('KeySpec') not in KEY_SPECS:
            raise NoData('KMS key has an unknown key spec')
        if metadata.get('KeyUsage') not in KEY_USAGES:
            raise NoData('KMS key has an unknown usage')
        if metadata.get('Origin') not in KEY_ORIGINS:
            raise NoData('KMS key has an unknown origin')
        store_id = metadata.get('CustomKeyStoreId')
        if store_id is not None and (not isinstance(store_id, str) or not store_id):
            raise NoData('KMS key has an invalid custom key store')
        result[key_id] = metadata
    return result


def customer_keys(ctx):
    """Return complete metadata for customer-managed keys in this Region."""
    return [key for key in keys(ctx).values()
            if key['KeyManager'] == 'CUSTOMER']


def aliases(key, ctx):
    found = _dedupe(
        ctx.call('kms', 'list_aliases', 'Aliases', KeyId=key['KeyId']),
        'AliasName', 'alias')
    for name, item in found.items():
        if not name.startswith('alias/') or name.startswith('alias/aws/'):
            raise NoData('KMS customer key has an invalid customer alias')
        _validate_arn(ctx, item.get('AliasArn'), name, 'alias')
        if item.get('TargetKeyId') != key['KeyId']:
            raise NoData('KMS alias has an inconsistent target key')
    return found


def grants(key, ctx):
    found = _dedupe(
        ctx.call('kms', 'list_grants', 'Grants', KeyId=key['KeyId']),
        'GrantId', 'grant')
    if any(item.get('KeyId') not in {key['KeyId'], key['Arn']}
           for item in found.values()):
        raise NoData('KMS grant has an inconsistent target key')
    return found


def custom_key_stores(ctx):
    found = _dedupe(
        ctx.call('kms', 'describe_custom_key_stores', 'CustomKeyStores'),
        'CustomKeyStoreId', 'custom key store')
    for item in found.values():
        store_type = item.get('CustomKeyStoreType', 'AWS_CLOUDHSM')
        state = item.get('ConnectionState')
        if store_type not in STORE_TYPES:
            raise NoData('KMS custom key store has an unknown type')
        if state not in STORE_STATES:
            raise NoData('KMS custom key store has an unknown state')
    return found


def rotation_count(key, ctx):
    rotations = _dedupe(
        ctx.call('kms', 'list_key_rotations', 'Rotations', KeyId=key['KeyId']),
        'KeyMaterialId', 'key rotation')
    count = 0
    for material_id, item in rotations.items():
        if len(material_id) != 64 or any(char not in '0123456789abcdef'
                                         for char in material_id):
            raise NoData('KMS key rotation has an invalid material identity')
        if item.get('KeyId') != key['KeyId']:
            raise NoData('KMS key rotation has an inconsistent key')
        if item.get('KeyMaterialState') not in MATERIAL_STATES:
            raise NoData('KMS key rotation has an unknown material state')
        if item.get('RotationType') not in ROTATION_TYPES:
            raise NoData('KMS key rotation has an unknown rotation type')
        count += item['RotationType'] == 'ON_DEMAND'

    # Accepted rotations consume the quota before they appear in the completed list.
    if key['KeyState'] == 'Enabled':
        status = ctx.call('kms', 'get_key_rotation_status', KeyId=key['KeyId'])
        if not isinstance(status, dict) or status.get('KeyId') != key['KeyId']:
            raise NoData('KMS key rotation status has an inconsistent key')
        count += status.get('OnDemandRotationStartDate') is not None
    return count


def on_demand_rotations_per_key(ctx):
    eligible = [key for key in customer_keys(ctx)
                if key['KeySpec'] == 'SYMMETRIC_DEFAULT'
                and key['Origin'] in {'AWS_KMS', 'EXTERNAL'}
                and 'CustomKeyStoreId' not in key]
    return maximum(
        ((key['Arn'], rotation_count(key, ctx), None) for key in eligible),
        'KMSKey', 'kms:ListKeys+DescribeKey+ListKeyRotations+'
        'GetKeyRotationStatus')


CHECKS = [
    ('L-C2F1777E', 'Customer Master Keys (CMKs)',
     lambda ctx: dict(usage=len(customer_keys(ctx)),
                      source='kms:ListKeys+DescribeKey',
                      method='ACCOUNT_COUNT')),
    ('L-340F62FB', 'Aliases per CMK',
     lambda ctx: maximum(
         ((key['Arn'], len(aliases(key, ctx)), None)
          for key in customer_keys(ctx)),
         'KMSKey', 'kms:ListKeys+DescribeKey+ListAliases')),
    ('L-D594A657', 'Grants per CMK',
     lambda ctx: maximum(
         ((key['Arn'], len(grants(key, ctx)), None)
          for key in customer_keys(ctx)),
         'KMSKey', 'kms:ListKeys+DescribeKey+ListGrants')),
    ('L-F33DCFEB', 'Custom Key Stores',
     lambda ctx: dict(usage=len(custom_key_stores(ctx)),
                      source='kms:DescribeCustomKeyStores',
                      method='ACCOUNT_COUNT')),
    ('L-0E66C9C0', 'On-demand rotations per CMK',
     on_demand_rotations_per_key),
]


def get_current_quotastatus_kms(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kms' for service, _ in context.quotas):
        return []
    return context.run('kms', CHECKS, skip)
