"""Amazon Transcribe regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('transcribe', method, key)),
                source=f'transcribe:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-3278D334', 'Total number of vocabularies per account',
     lambda ctx: resource_count(ctx, 'list_vocabularies', 'Vocabularies')),
    ('L-79BBEFC1', 'Total number of medical vocabularies per account',
     lambda ctx: resource_count(ctx, 'list_medical_vocabularies', 'Vocabularies')),
    ('L-BE7BEF67', 'Maximum number of vocabulary filters',
     lambda ctx: resource_count(ctx, 'list_vocabulary_filters', 'VocabularyFilters')),
    ('L-9190489D', 'Total number of custom language models per account',
     lambda ctx: resource_count(ctx, 'list_language_models', 'Models')),
]


def get_current_quotastatus_transcribe(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'transcribe' for service, _ in context.quotas):
        return []
    return context.run('transcribe', CHECKS, skip)
