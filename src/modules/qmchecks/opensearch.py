"""OpenSearch Service and OpenSearch Applications inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def get_current_quotastatus_opensearch(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'es' for service, _ in context.quotas):
        entries.extend(context.run('es', [
            ('L-076D529E', 'Domains per Region',
             lambda c: dict(usage=len(c.call('es', 'list_domain_names', 'DomainNames')),
                            source='es:ListDomainNames', method='ACCOUNT_COUNT')),
        ], skip))
    if any(service == 'opensearch' for service, _ in context.quotas):
        entries.extend(context.run('opensearch', [
            ('L-B9142967', 'OpenSearch Applications per region',
             lambda c: dict(usage=len(c.call('opensearch', 'list_applications', 'ApplicationSummaries')),
                            source='opensearch:ListApplications', method='ACCOUNT_COUNT')),
        ], skip))
    return entries
