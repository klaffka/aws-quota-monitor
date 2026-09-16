"""Amazon Textract adapter and adapter version inventories."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

TEXTRACT = 'textract'
VERSION_STATES = {'ACTIVE', 'AT_RISK', 'DEPRECATED', 'CREATION_ERROR',
                  'CREATION_IN_PROGRESS'}


def in_progress_adapter_versions(ctx):
    usage = 0
    for version in ctx.call(TEXTRACT, 'list_adapter_versions', 'AdapterVersions'):
        status = version.get('Status')
        if status not in VERSION_STATES:
            raise NoData('Textract adapter version has an unknown status')
        usage += status == 'CREATION_IN_PROGRESS'
    return dict(usage=usage, source='textract:ListAdapterVersions',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-C9EC1D79', 'Adapters per account',
     lambda ctx: dict(usage=len(ctx.call(TEXTRACT, 'list_adapters', 'Adapters')),
                      source='textract:ListAdapters', method='ACCOUNT_COUNT')),
    ('L-E6985921', 'In-progress adapter versions per account',
     in_progress_adapter_versions),
]


def get_current_quotastatus_textract(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'textract' for service, _ in context.quotas):
        return []
    return context.run('textract', CHECKS, skip)
