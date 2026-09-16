"""Elastic Beanstalk regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-1CEABD17', 'Applications',
     lambda c: dict(usage=len(c.call('elasticbeanstalk', 'describe_applications', 'Applications')),
                    source='elasticbeanstalk:DescribeApplications', method='ACCOUNT_COUNT')),
    ('L-8EFC1C51', 'Environments',
     lambda c: dict(usage=len(c.call('elasticbeanstalk', 'describe_environments', 'Environments')),
                    source='elasticbeanstalk:DescribeEnvironments', method='ACCOUNT_COUNT')),
    ('L-D64F1F14', 'Application versions',
     lambda c: dict(usage=len(c.call('elasticbeanstalk', 'describe_application_versions', 'ApplicationVersions')),
                    source='elasticbeanstalk:DescribeApplicationVersions', method='ACCOUNT_COUNT')),
    ('L-E593A077', 'Custom platform versions',
     lambda c: dict(usage=len(c.call('elasticbeanstalk', 'list_platform_versions', 'PlatformSummaryList',
                                     Filters=[{'Operator': '=', 'Type': 'PlatformStatus', 'Values': ['Ready']}])) ,
                    source='elasticbeanstalk:ListPlatformVersions', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_elasticbeanstalk(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'elasticbeanstalk' for service, _ in context.quotas):
        return []
    return context.run('elasticbeanstalk', CHECKS, skip)
