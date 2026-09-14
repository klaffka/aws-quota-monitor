"""OpenSearch Service and OpenSearch UI application inventories."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env


DOMAIN_CHECKS = [
    ('L-076D529E', 'Domains per Region',
     lambda c: dict(usage=len(c.call('es', 'list_domain_names', 'DomainNames')),
                    source='es:ListDomainNames', method='ACCOUNT_COUNT')),
]

APPLICATION_STATES = {'CREATING', 'UPDATING', 'DELETING', 'ACTIVE', 'FAILED'}


def application_count(ctx):
    applications = {}
    arns = set()
    for item in ctx.call('opensearch', 'list_applications', 'ApplicationSummaries'):
        if not isinstance(item, dict):
            raise NoData('OpenSearch UI application inventory contains an invalid item')
        identity = item.get('id')
        arn = item.get('arn')
        if (not isinstance(identity, str) or not identity
                or not isinstance(arn, str) or not arn
                or item.get('status') not in APPLICATION_STATES):
            raise NoData('OpenSearch UI application is missing required identity data')
        if identity in applications:
            if applications[identity] != item:
                raise NoData('OpenSearch UI application changed during pagination')
            continue
        if arn in arns:
            raise NoData('OpenSearch UI application inventory contains a duplicate ARN')
        applications[identity] = item
        arns.add(arn)
    return dict(usage=len(applications), source='opensearch:ListApplications',
                method='ACCOUNT_COUNT')


APPLICATION_CHECKS = [
    ('L-B9142967', 'OpenSearch Applications per region', application_count),
]

CUSTOM_KEYS = {
    ('es', DOMAIN_CHECKS[0][0]),
    ('opensearch', APPLICATION_CHECKS[0][0]),
}


def get_current_quotastatus_opensearch(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    if any(service == 'es' for service, _ in context.quotas):
        entries.extend(context.run('es', DOMAIN_CHECKS, skip))
    if any(service == 'opensearch' for service, _ in context.quotas):
        entries.extend(context.run('opensearch', APPLICATION_CHECKS, skip))
    return entries
