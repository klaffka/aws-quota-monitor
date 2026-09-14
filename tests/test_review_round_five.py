from unittest.mock import Mock

from modules.qmchecks.kms import CHECKS


def test_kms_parent_quotas_count_aliases_and_grants_per_customer_key():
    account = '123456789012'
    region = 'eu-central-1'
    arn = f'arn:aws:kms:{region}:{account}:key/key-1'
    ctx = Mock(account=account, region=region)
    values = {
        'list_keys': [{'KeyId': 'key-1', 'KeyArn': arn}],
        'describe_key': {'KeyMetadata': {
            'KeyId': 'key-1', 'Arn': arn, 'KeyManager': 'CUSTOMER',
            'KeyState': 'Enabled', 'KeySpec': 'SYMMETRIC_DEFAULT',
            'KeyUsage': 'ENCRYPT_DECRYPT', 'Origin': 'AWS_KMS'}},
        'list_aliases': [{
            'AliasName': 'alias/one',
            'AliasArn': f'arn:aws:kms:{region}:{account}:alias/one',
            'TargetKeyId': 'key-1'}],
        'list_grants': [{'GrantId': 'grant', 'KeyId': 'key-1'}],
    }
    ctx.call.side_effect = lambda _service, method, *_args, **_kwargs: values[method]
    assert CHECKS[1][2](ctx)['usage'] == 1
    assert CHECKS[2][2](ctx)['usage'] == 1
