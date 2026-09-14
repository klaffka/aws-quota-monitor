"""Application Migration Service regional application inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-D5507441', 'Max active applications',
           lambda ctx: dict(usage=sum(not app.get('isArchived', False)
                                      for app in ctx.call('mgn', 'describe_applications', 'items')),
                            source='mgn:DescribeApplications', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_mgn(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mgn' for service, _ in context.quotas): return []
    return context.run('mgn', CHECKS, skip)
