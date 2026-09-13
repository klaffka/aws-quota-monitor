"""Amazon Omics regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('omics', method, key)), source=f'omics:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-7CAE62CF', 'Maximum workflows',
     lambda ctx: resource_count(ctx, 'list_workflows', 'items')),
    ('L-BFFBB2FD', 'Maximum sequence stores',
     lambda ctx: resource_count(ctx, 'list_sequence_stores', 'sequenceStores')),
    ('L-899DA104', 'Maximum variant stores',
     lambda ctx: resource_count(ctx, 'list_variant_stores', 'variantStores')),
    ('L-01A419C5', 'Maximum annotation stores',
     lambda ctx: resource_count(ctx, 'list_annotation_stores', 'annotationStores')),
]


def get_current_quotastatus_omics(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'omics' for service, _ in context.quotas):
        return []
    return context.run('omics', CHECKS, skip)
