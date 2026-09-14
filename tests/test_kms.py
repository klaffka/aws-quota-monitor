import pytest

from modules.qmchecks import kms
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def key(identifier, *, manager='CUSTOMER', spec='SYMMETRIC_DEFAULT',
        origin='AWS_KMS', state='Enabled', **fields):
    arn = f'arn:aws:kms:{REGION}:{ACCOUNT}:key/{identifier}'
    return ({'KeyId': identifier, 'KeyArn': arn},
            {'KeyId': identifier, 'Arn': arn, 'KeyManager': manager,
             'KeyState': state, 'KeySpec': spec,
             'KeyUsage': ('ENCRYPT_DECRYPT' if spec == 'SYMMETRIC_DEFAULT'
                          else 'SIGN_VERIFY'),
             'Origin': origin, **fields})


def alias(identifier, key_id):
    name = f'alias/{identifier}'
    return {'AliasName': name,
            'AliasArn': f'arn:aws:kms:{REGION}:{ACCOUNT}:{name}',
            'TargetKeyId': key_id}


def grant(identifier, key_id):
    return {'GrantId': identifier, 'KeyId': key_id}


def rotation(material, key_id, kind):
    return {'KeyMaterialId': material * 64, 'KeyId': key_id,
            'KeyMaterialState': 'NON_CURRENT', 'RotationType': kind}


class Context:
    account = ACCOUNT
    region = REGION

    def __init__(self, responses):
        self.responses = responses

    def call(self, service, method, key=None, **kwargs):
        assert service == 'kms'
        return self.responses.get((method, tuple(sorted(kwargs.items()))),
                                  [] if key else {})


def populated_context():
    listed_one, one = key('key-one')
    listed_two, two = key('key-two', spec='RSA_2048')
    listed_aws, aws = key('key-aws', manager='AWS')
    responses = {
        ('list_keys', ()): [listed_one, listed_two, listed_aws],
        ('describe_key', (('KeyId', 'key-one'),)): {'KeyMetadata': one},
        ('describe_key', (('KeyId', 'key-two'),)): {'KeyMetadata': two},
        ('describe_key', (('KeyId', 'key-aws'),)): {'KeyMetadata': aws},
        ('list_aliases', (('KeyId', 'key-one'),)): [
            alias('one', 'key-one'), alias('two', 'key-one')],
        ('list_aliases', (('KeyId', 'key-two'),)): [alias('three', 'key-two')],
        ('list_grants', (('KeyId', 'key-one'),)): [grant('grant-one', 'key-one')],
        ('list_grants', (('KeyId', 'key-two'),)): [
            grant('grant-two', 'key-two'), grant('grant-three', 'key-two'),
            grant('grant-four', 'key-two')],
        ('describe_custom_key_stores', ()): [
            {'CustomKeyStoreId': 'cks-one', 'CustomKeyStoreType': 'AWS_CLOUDHSM',
             'ConnectionState': 'CONNECTED'},
            {'CustomKeyStoreId': 'cks-two',
             'CustomKeyStoreType': 'EXTERNAL_KEY_STORE',
             'ConnectionState': 'DISCONNECTED'}],
        ('list_key_rotations', (('KeyId', 'key-one'),)): [
            rotation('a', 'key-one', 'AUTOMATIC'),
            rotation('b', 'key-one', 'ON_DEMAND'),
            rotation('c', 'key-one', 'ON_DEMAND')],
        ('get_key_rotation_status', (('KeyId', 'key-one'),)): {
            'KeyId': 'key-one', 'OnDemandRotationStartDate': 'pending'},
    }
    return Context(responses)


def test_all_kms_resource_quota_counts():
    results = [check(populated_context()) for _code, _name, check in kms.CHECKS]
    assert [result['usage'] for result in results] == [2, 2, 3, 2, 3]
    assert results[-1]['resource_id'].endswith('key/key-one')


def test_all_kms_resource_checks_are_registered():
    expected = {('kms', code) for code, _name, _check in kms.CHECKS}
    assert expected <= custom_keys()


def test_kms_does_not_assume_a_missing_key_manager_is_customer_owned():
    listed, metadata = key('key-one')
    metadata.pop('KeyManager')
    ctx = Context({
        ('list_keys', ()): [listed],
        ('describe_key', (('KeyId', 'key-one'),)): {'KeyMetadata': metadata},
    })
    with pytest.raises(NoData, match='unknown manager'):
        kms.customer_keys(ctx)


def test_kms_rejects_changed_rotation_duplicates():
    ctx = populated_context()
    lookup = ('list_key_rotations', (('KeyId', 'key-one'),))
    duplicate = {**ctx.responses[lookup][0], 'RotationType': 'ON_DEMAND'}
    ctx.responses[lookup].append(duplicate)
    one = kms.customer_keys(ctx)[0]
    with pytest.raises(NoData, match='changed during pagination'):
        kms.rotation_count(one, ctx)
