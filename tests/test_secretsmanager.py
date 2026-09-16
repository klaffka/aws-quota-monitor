from unittest.mock import Mock

from modules.qmchecks.secretsmanager import CHECKS


def test_secretsmanager_secret_inventory_is_counted():
    ctx = Mock()
    ctx.call.return_value = [{'ARN': 'arn:secret:one'}, {'ARN': 'arn:secret:two'}]
    result = CHECKS[0][2](ctx)
    assert result['usage'] == 2
    assert ctx.call.call_args.args[:3] == ('secretsmanager', 'list_secrets', 'SecretList')


def test_secretsmanager_versions_use_maximum_per_secret():
    from modules.qmchecks.secretsmanager import versions_per_secret
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ARN': 'arn:one'}, {'ARN': 'arn:two'}],
        [{'VersionId': '1'}, {'VersionId': '2'}],
        [{'VersionId': '1'}],
    ]
    result = versions_per_secret(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:one')
