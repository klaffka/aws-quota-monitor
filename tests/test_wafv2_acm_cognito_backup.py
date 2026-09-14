from unittest.mock import Mock

from modules.qmchecks.wafv2 import CHECKS as WAF_CHECKS
from modules.qmchecks.acm import CHECKS as ACM_CHECKS
from modules.qmchecks.cognito import CHECKS as COGNITO_CHECKS
from modules.qmchecks.backup import CHECKS as BACKUP_CHECKS


def test_wafv2_regional_resource_counts_use_scope():
    ctx = Mock()
    ctx.call.return_value = [{'Id': 'one'}, {'Id': 'two'}]
    assert WAF_CHECKS[0][2](ctx)['usage'] == 2
    assert ctx.call.call_args.kwargs['Scope'] == 'REGIONAL'


def test_acm_and_cognito_counts_use_paginated_inventories():
    ctx = Mock()
    ctx.call.side_effect = [[{'CertificateArn': 'arn:one'}], [{'Id': 'pool-1'}, {'Id': 'pool-2'}]]
    assert ACM_CHECKS[0][2](ctx)['usage'] == 1
    assert COGNITO_CHECKS[0][2](ctx)['usage'] == 2


def test_backup_resource_counts_are_separate_from_rate_quotas():
    ctx = Mock()
    ctx.call.side_effect = [[{'BackupVaultName': 'vault'}], [{'BackupPlanId': 'plan'}],
                            [{'FrameworkName': 'framework'}], [{'ReportPlanName': 'report'}]]
    assert [check[2](ctx)['usage'] for check in BACKUP_CHECKS[:4]] == [1, 1, 1, 1]
