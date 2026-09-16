from unittest.mock import Mock

from modules.qmchecks.transfer import users_per_server
from modules.qmchecks.backup import CHECKS as BACKUP_CHECKS, framework_controls, frameworks_per_report_plan
from modules.qmchecks.transfer import connectors_by_type


def test_transfer_users_per_server_uses_maximum():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ServerId': 's1'}, {'ServerId': 's2'}],
        [{}, {}], [{}],
    ]
    result = users_per_server(ctx)
    assert result['usage'] == 2 and result['resource_id'] == 's1'


def by_code(code):
    return next(fn for quota, _name, fn in BACKUP_CHECKS if quota == code)


def test_backup_recovery_points_and_plan_versions():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'BackupVaultName': 'v1'}], [{'RecoveryPointArn': 'r1'}, {'RecoveryPointArn': 'r2'}],
    ]
    assert by_code('L-514878B6')(ctx)['usage'] == 2
    ctx.call.side_effect = [
        [{'BackupPlanId': 'p1'}], [{'VersionId': '1'}, {'VersionId': '2'}, {'VersionId': '3'}],
    ]
    assert by_code('L-9122A82F')(ctx)['usage'] == 3


def test_backup_framework_controls_and_report_plan_frameworks_are_counted():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'FrameworkName': 'framework'}], {'FrameworkControls': [{'ControlName': 'one'}, {'ControlName': 'two'}]},
        [{'ReportPlanName': 'plan'}], {'ReportPlan': {'ReportSetting': {'NumberOfFrameworks': 3}}},
    ]
    assert framework_controls(ctx)['usage'] == 2
    assert frameworks_per_report_plan(ctx)['usage'] == 3


def test_transfer_connectors_are_counted_by_type():
    ctx = Mock()
    ctx.call.return_value = [{'ConnectorType': 'AS2'}, {'ConnectorType': 'SFTP'}, {'ConnectorType': 'AS2'}]
    assert connectors_by_type(ctx, 'AS2')['usage'] == 2


def test_transfer_logical_directory_mappings_use_maximum_per_user():
    from modules.qmchecks.transfer import logical_directory_mappings_per_user
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ServerId': 's1'}],
        [{'UserName': 'u1'}, {'UserName': 'u2'}],
        {'User': {'HomeDirectoryDetails': [{}, {}]}},
        {'User': {'HomeDirectoryDetails': [{}]}},
    ]
    assert logical_directory_mappings_per_user(ctx)['usage'] == 2
