"""AWS Backup regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


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


# A job holds its slot from the moment Backup accepts it until it finishes, so
# every state before a terminal one counts. The listing filters by exactly one
# state at a time, which is why each is asked for separately.
BACKUP_IN_FLIGHT = ('CREATED', 'PENDING', 'RUNNING')
COPY_IN_FLIGHT = ('CREATED', 'RUNNING')


def _in_flight(ctx, method, key, states, field, what):
    counts = {}
    for state in states:
        for job in ctx.call('backup', method, key, ByState=state):
            parent = job.get(field)
            if not isinstance(parent, str) or not parent:
                raise NoData(f'AWS Backup job has no {what}')
            counts[parent] = counts.get(parent, 0) + 1
    return counts


def backup_jobs_per_resource(ctx):
    counts = _in_flight(ctx, 'list_backup_jobs', 'BackupJobs', BACKUP_IN_FLIGHT,
                        'ResourceArn', 'resource')
    return maximum([(arn, count, None) for arn, count in sorted(counts.items())],
                   'BackupResource', 'backup:ListBackupJobs')


def copy_jobs_per_service(ctx):
    """The quota is per supported service, which the job names as its type."""
    counts = _in_flight(ctx, 'list_copy_jobs', 'CopyJobs', COPY_IN_FLIGHT,
                        'ResourceType', 'resource type')
    return maximum([(kind, count, None) for kind, count in sorted(counts.items())],
                   'BackupResourceType', 'backup:ListCopyJobs')


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
    ('L-366B61FD', 'Concurrent backup jobs per resource', backup_jobs_per_resource),
    ('L-FFD6444F', 'Concurrent backup copies per supported service per account',
     copy_jobs_per_service),
]


def get_current_quotastatus_backup(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'backup' for service, _ in context.quotas):
        return []
    return context.run('backup', CHECKS, skip)
