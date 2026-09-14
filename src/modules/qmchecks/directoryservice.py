"""AWS Directory Service directory inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


def directories(ctx):
    return ctx.call('ds', 'describe_directories', 'DirectoryDescriptions')


def directory_count(ctx, directory_type):
    return dict(usage=sum(d.get('Type') == directory_type for d in directories(ctx)),
                source='ds:DescribeDirectories', method='ACCOUNT_COUNT',
                meta={'directoryType': directory_type})


CHECKS = [
    ('L-EF86B739', 'AWS Managed Microsoft AD directories',
     lambda ctx: directory_count(ctx, 'MicrosoftAD')),
    ('L-092080C3', 'AD Connector directories',
     lambda ctx: directory_count(ctx, 'ADConnector')),
]


def get_current_quotastatus_directoryservice(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ds' for service, _ in context.quotas):
        return []
    return context.run('ds', CHECKS, skip)
