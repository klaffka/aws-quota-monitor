"""MediaConvert regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-44E8E4BC', 'Queues per AWS Region',
     lambda c: dict(usage=len(c.call('mediaconvert', 'list_queues', 'Queues')),
                    source='mediaconvert:ListQueues', method='ACCOUNT_COUNT')),
    ('L-FFA964F8', 'Custom job templates',
     lambda c: dict(usage=len(c.call('mediaconvert', 'list_job_templates', 'JobTemplates')),
                    source='mediaconvert:ListJobTemplates', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_mediaconvert(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediaconvert' for service, _ in context.quotas):
        return []
    return context.run('mediaconvert', CHECKS, skip)
