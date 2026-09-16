"""AWS Backup regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.aws import maximum


def count(ctx, method, key):
    return dict(usage=len(ctx.call('backup', method, key)),
                source=f'backup:{method}', method='ACCOUNT_COUNT')


def framework_controls(ctx):
    total = 0
    for framework in ctx.call('backup', 'list_frameworks', 'Frameworks'):
        name = framework.get('FrameworkName')
        if name:
            details = ctx.call('backup', 'describe_framework', FrameworkName=name)
            total += len(details.get('FrameworkControls', []))
    return dict(usage=total, source='backup:ListFrameworks+DescribeFramework', method='ACCOUNT_COUNT')


def frameworks_per_report_plan(ctx):
    values = []
    for plan in ctx.call('backup', 'list_report_plans', 'ReportPlans'):
        name = plan.get('ReportPlanName')
        if name:
            details = ctx.call('backup', 'describe_report_plan', ReportPlanName=name)
            setting = details.get('ReportPlan', {}).get('ReportSetting', {})
            values.append((name, setting.get('NumberOfFrameworks', len(setting.get('FrameworkArns', []))), None))
    return maximum(values, 'BackupReportPlan', 'backup:ListReportPlans+DescribeReportPlan')


CHECKS = [
    ('L-7705D2CB', 'Backup vaults per Region per account',
     lambda ctx: count(ctx, 'list_backup_vaults', 'BackupVaultList')),
    ('L-BD69F607', 'Backup plans per Region per account',
     lambda ctx: count(ctx, 'list_backup_plans', 'BackupPlansList')),
    ('L-E43E0ED6', 'Frameworks per Region per account',
     lambda ctx: count(ctx, 'list_frameworks', 'Frameworks')),
    ('L-C296F1F5', 'Report plans per Region per account',
     lambda ctx: count(ctx, 'list_report_plans', 'ReportPlans')),
    ('L-514878B6', 'Recovery points per backup vault',
     lambda ctx: maximum([(v.get('BackupVaultName'), len(ctx.call(
         'backup', 'list_recovery_points_by_backup_vault', 'RecoveryPoints',
         BackupVaultName=v.get('BackupVaultName'))), None)
         for v in ctx.call('backup', 'list_backup_vaults', 'BackupVaultList')],
         'BackupVault', 'backup:ListRecoveryPointsByBackupVault')),
    ('L-9122A82F', 'Versions per backup plan',
     lambda ctx: maximum([(p.get('BackupPlanId'), len(ctx.call(
         'backup', 'list_backup_plan_versions', 'BackupPlanVersionsList', BackupPlanId=p.get('BackupPlanId'))), None)
         for p in ctx.call('backup', 'list_backup_plans', 'BackupPlansList')],
         'BackupPlan', 'backup:ListBackupPlanVersions')),
    ('L-B4021FB0', 'Framework controls per Region per account', framework_controls),
    ('L-9CAF0B92', 'Frameworks per report plan', frameworks_per_report_plan),
]


def get_current_quotastatus_backup(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'backup' for service, _ in context.quotas):
        return []
    return context.run('backup', CHECKS, skip)
