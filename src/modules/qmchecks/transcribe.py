"""Amazon Transcribe vocabulary, model, job and category quotas.

The audio file, vocabulary and phrase size quotas bound a single input, the
minimum duration quotas state a floor, the job record retention quotas name a
period, and the streaming quotas count live HTTP/2 and WebSocket sessions that
no API lists.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

TRANSCRIBE = 'transcribe'
JOB_STATES = {'QUEUED', 'IN_PROGRESS', 'FAILED', 'COMPLETED'}
RUNNING_JOB_STATES = ('QUEUED', 'IN_PROGRESS')
VOCABULARY_STATES = {'PENDING', 'READY', 'FAILED'}
MODEL_STATES = {'IN_PROGRESS', 'FAILED', 'COMPLETED'}


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call(TRANSCRIBE, method, key)),
                source=f'transcribe:{method}', method='ACCOUNT_COUNT')


def _running_jobs(method, key, source):
    """Ask Transcribe for each unfinished status, which it filters server side."""
    def check(ctx):
        usage = 0
        for status in RUNNING_JOB_STATES:
            for job in ctx.call(TRANSCRIBE, method, key, Status=status):
                reported = job.get('TranscriptionJobStatus') or job.get('CallAnalyticsJobStatus')
                if reported is not None and reported not in JOB_STATES:
                    raise NoData('Transcribe job has an unknown status')
                usage += 1
        return dict(usage=usage, source=source, method='ACCOUNT_COUNT')
    return check


def _pending_vocabularies(method, source):
    def check(ctx):
        usage = 0
        for vocabulary in ctx.call(TRANSCRIBE, method, 'Vocabularies',
                                   StateEquals='PENDING'):
            if vocabulary.get('VocabularyState') not in VOCABULARY_STATES:
                raise NoData('Transcribe vocabulary has an unknown state')
            usage += 1
        return dict(usage=usage, source=source, method='ACCOUNT_COUNT')
    return check


def training_language_models(ctx):
    usage = 0
    for model in ctx.call(TRANSCRIBE, 'list_language_models', 'Models',
                          StatusEquals='IN_PROGRESS'):
        if model.get('ModelStatus') not in MODEL_STATES:
            raise NoData('Transcribe language model has an unknown status')
        usage += 1
    return dict(usage=usage, source='transcribe:ListLanguageModels',
                method='ACCOUNT_COUNT')


def rules_per_category(ctx):
    values = []
    for category in ctx.call(TRANSCRIBE, 'list_call_analytics_categories',
                             'Categories'):
        name = category.get('CategoryName')
        if not isinstance(name, str) or not name:
            raise NoData('Call Analytics category is missing its name')
        rules = category.get('Rules')
        if not isinstance(rules, list):
            raise NoData('Call Analytics category has no rules')
        values.append((name, len(rules), None))
    return maximum(values, 'CallAnalyticsCategory',
                   'transcribe:ListCallAnalyticsCategories')


TRANSCRIPTION_JOBS = _running_jobs('list_transcription_jobs',
                                   'TranscriptionJobSummaries',
                                   'transcribe:ListTranscriptionJobs')
MEDICAL_JOBS = _running_jobs('list_medical_transcription_jobs',
                             'MedicalTranscriptionJobSummaries',
                             'transcribe:ListMedicalTranscriptionJobs')
ANALYTICS_JOBS = _running_jobs('list_call_analytics_jobs',
                               'CallAnalyticsJobSummaries',
                               'transcribe:ListCallAnalyticsJobs')
PENDING_VOCABULARIES = _pending_vocabularies('list_vocabularies',
                                             'transcribe:ListVocabularies')
PENDING_MEDICAL_VOCABULARIES = _pending_vocabularies(
    'list_medical_vocabularies', 'transcribe:ListMedicalVocabularies')

CHECKS = [
    ('L-3278D334', 'Total number of vocabularies per account',
     lambda ctx: resource_count(ctx, 'list_vocabularies', 'Vocabularies')),
    ('L-CB43679D', 'Total vocabulary limit',
     lambda ctx: resource_count(ctx, 'list_vocabularies', 'Vocabularies')),
    ('L-79BBEFC1', 'Total number of medical vocabularies per account',
     lambda ctx: resource_count(ctx, 'list_medical_vocabularies', 'Vocabularies')),
    ('L-68305688', 'Total medical vocabulary limit',
     lambda ctx: resource_count(ctx, 'list_medical_vocabularies', 'Vocabularies')),
    ('L-BE7BEF67', 'Maximum number of vocabulary filters',
     lambda ctx: resource_count(ctx, 'list_vocabulary_filters', 'VocabularyFilters')),
    ('L-9190489D', 'Total number of custom language models per account',
     lambda ctx: resource_count(ctx, 'list_language_models', 'Models')),
    ('L-866105CB', 'Total language model limit',
     lambda ctx: resource_count(ctx, 'list_language_models', 'Models')),
    ('L-A51A98B4', 'Number of pending vocabularies', PENDING_VOCABULARIES),
    ('L-0E2548E4', 'Number of concurrent vocabulary jobs', PENDING_VOCABULARIES),
    ('L-340B75E2', 'Number of pending medical vocabularies',
     PENDING_MEDICAL_VOCABULARIES),
    ('L-9CDB9A91', 'Number of concurrent medical vocabulary jobs',
     PENDING_MEDICAL_VOCABULARIES),
    ('L-58D7221C', 'Number of concurrent transcription jobs', TRANSCRIPTION_JOBS),
    ('L-6F7AB1C9', 'Number of concurrent batch transcription jobs',
     TRANSCRIPTION_JOBS),
    ('L-B882C824', 'Number of concurrent medical transcription jobs', MEDICAL_JOBS),
    ('L-63F366BB', 'Number of concurrent medical batch transcription jobs',
     MEDICAL_JOBS),
    ('L-BAA3E542', 'Number of concurrent analytics jobs', ANALYTICS_JOBS),
    ('L-48FC5F8A', 'Number of concurrent Call Analytics batch jobs', ANALYTICS_JOBS),
    ('L-B4C1AD62', 'Number of concurrent language models', training_language_models),
    ('L-E0D2ADDE', 'Number of concurrently training custom language models',
     training_language_models),
    ('L-E3EBEDF2', 'Maximum number of categories for Call Analytics batch jobs',
     lambda ctx: resource_count(ctx, 'list_call_analytics_categories', 'Categories')),
    ('L-2E269322', 'Maximum number of rules per category for Call Analytics batch jobs',
     rules_per_category),
]


def get_current_quotastatus_transcribe(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'transcribe' for service, _ in context.quotas):
        return []
    return context.run('transcribe', CHECKS, skip)
