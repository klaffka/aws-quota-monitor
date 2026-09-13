"""AWS License Manager regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-CDB75D7A', 'License configurations',
     lambda c: dict(usage=len(c.call('license-manager', 'list_license_configurations', 'LicenseConfigurations')),
                    source='license-manager:ListLicenseConfigurations', method='ACCOUNT_COUNT')),
    ('L-9FBEFBCB', 'Report generators',
     lambda c: dict(usage=len(c.call('license-manager', 'list_license_manager_report_generators', 'ReportGenerators')),
                    source='license-manager:ListLicenseManagerReportGenerators', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_license_manager(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'license-manager' for service, _ in context.quotas):
        return []
    return context.run('license-manager', CHECKS, skip)
