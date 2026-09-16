from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks.payment_cryptography import CHECKS, alias_count
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '111111111111'
REGION = 'eu-central-1'
KEY_ARN = f'arn:aws:payment-cryptography:{REGION}:{ACCOUNT}:key/key-one'


def context(items):
    ctx = Mock(account=ACCOUNT, region=REGION)
    ctx.call.return_value = items
    return ctx


def test_payment_cryptography_alias_count_deduplicates_identical_pages():
    alias = {'AliasName': 'alias/checkout', 'KeyArn': KEY_ARN}
    result = alias_count(context([alias, dict(alias), {'AliasName': 'alias/backup'}]))
    assert result['usage'] == 2


def test_payment_cryptography_alias_count_rejects_invalid_items():
    for items, match in [([None], 'invalid item'),
                         ([{'AliasName': 'checkout'}], 'invalid name'),
                         ([{'AliasName': 'alias/checkout',
                            'KeyArn': KEY_ARN.replace(REGION, 'eu-west-1')}],
                          'inconsistent key ARN')]:
        with pytest.raises(NoData, match=match):
            alias_count(context(items))


def test_payment_cryptography_alias_count_rejects_conflicting_pages():
    aliases = [{'AliasName': 'alias/checkout', 'KeyArn': KEY_ARN},
               {'AliasName': 'alias/checkout'}]
    with pytest.raises(NoData, match='changed during pagination'):
        alias_count(context(aliases))


def test_payment_cryptography_alias_check_is_registered_with_read_permission():
    assert ('payment-cryptography', 'L-10DEBB19') in custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"payment-cryptography:ListAliases"' in policy
