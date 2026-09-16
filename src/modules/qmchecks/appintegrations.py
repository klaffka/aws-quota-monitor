"""Amazon AppIntegrations regional application counts."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def associations_per_parent(ctx, parent_method, parent_key, child_method, child_key,
                            parent_field, argument):
    values = []
    for parent in ctx.call('appintegrations', parent_method, parent_key):
        name = parent.get(parent_field)
        if name:
            values.append((name, len(ctx.call('appintegrations', child_method, child_key,
                                              **{argument: name})), None))
    return maximum(values, 'AppIntegration', f'appintegrations:{child_method}')


CHECKS = [
    ('L-8C721859', 'Applications per Region',
     lambda c: dict(usage=len(c.call('appintegrations', 'list_applications', 'Applications')),
                    source='appintegrations:ListApplications', method='ACCOUNT_COUNT')),
    ('L-152D3E9E', 'Event integrations per Region',
     lambda c: dict(usage=len(c.call('appintegrations', 'list_event_integrations', 'EventIntegrations')),
                    source='appintegrations:ListEventIntegrations', method='ACCOUNT_COUNT')),
    ('L-013E1287', 'Data integrations per Region',
     lambda c: dict(usage=len(c.call('appintegrations', 'list_data_integrations', 'DataIntegrations')),
                    source='appintegrations:ListDataIntegrations', method='ACCOUNT_COUNT')),
    ('L-3DEFA101', 'Data integration associations per data integration',
     lambda c: associations_per_parent(c, 'list_data_integrations', 'DataIntegrations',
                                       'list_data_integration_associations',
                                       'DataIntegrationAssociations', 'Name', 'DataIntegrationIdentifier')),
    ('L-C1BC25C8', 'Event integration associations per event integration',
     lambda c: associations_per_parent(c, 'list_event_integrations', 'EventIntegrations',
                                       'list_event_integration_associations',
                                       'EventIntegrationAssociations', 'Name', 'EventIntegrationName')),
]


def get_current_quotastatus_appintegrations(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'app-integrations' for service, _ in context.quotas):
        return []
    return context.run('app-integrations', CHECKS, skip)
