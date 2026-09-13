"""AWS Entity Resolution regional workflow inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('entityresolution', method, key)), source=f'entityresolution:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-60DAF647', 'Matching workflows', lambda ctx: count(ctx, 'list_matching_workflows', 'workflows')),
    ('L-C5A3094C', 'ID mapping workflows', lambda ctx: count(ctx, 'list_id_mapping_workflows', 'workflows')),
    ('L-FBA1B7BB', 'ID namespaces', lambda ctx: count(ctx, 'list_id_namespaces', 'idNamespaces')),
    ('L-00E43259', 'Schema mappings', lambda ctx: count(ctx, 'list_schema_mappings', 'schemaMappings')),
]


def get_current_quotastatus_entityresolution(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'entityresolution' for service, _ in context.quotas): return []
    return context.run('entityresolution', CHECKS, skip)
