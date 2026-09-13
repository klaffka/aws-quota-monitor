"""Kinesis Data Analytics SQL application inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-3729A2EF', 'Application count',
     lambda ctx: dict(usage=len(ctx.call('kinesisanalytics', 'list_applications', 'ApplicationSummaries')),
                      source='kinesisanalytics:ListApplications', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_kinesisanalytics(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kinesisanalytics' for service, _ in context.quotas):
        return []
    return context.run('kinesisanalytics', CHECKS, skip)
