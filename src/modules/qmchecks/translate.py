"""Amazon Translate terminology and batch job quotas."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

TRANSLATE = 'translate'
JOB_STATES = {'SUBMITTED', 'IN_PROGRESS', 'COMPLETED', 'COMPLETED_WITH_ERROR',
              'FAILED', 'STOP_REQUESTED', 'STOPPED'}
RUNNING_STATES = {'SUBMITTED', 'IN_PROGRESS', 'STOP_REQUESTED'}


def concurrent_batch_jobs(ctx):
    usage = 0
    for job in ctx.call(TRANSLATE, 'list_text_translation_jobs',
                        'TextTranslationJobPropertiesList'):
        status = job.get('JobStatus')
        if status not in JOB_STATES:
            raise NoData('Translate job has an unknown status')
        usage += status in RUNNING_STATES
    return dict(usage=usage, source='translate:ListTextTranslationJobs',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-4011ABD8', 'Custom terminology files',
     lambda ctx: dict(usage=len(ctx.call(TRANSLATE, 'list_terminologies',
                                         'TerminologyPropertiesList')),
                      source='translate:ListTerminologies', method='ACCOUNT_COUNT')),
    ('L-10DB0BCF', 'Concurrent batch translation jobs', concurrent_batch_jobs),
]


def get_current_quotastatus_translate(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'translate' for service, _ in context.quotas):
        return []
    return context.run('translate', CHECKS, skip)
