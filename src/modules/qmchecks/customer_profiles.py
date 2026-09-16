"""Amazon Connect Customer Profiles domain, object type and recommender quotas.

Per-profile quotas (`Objects per profile`, `Maximum number of profile history
records per profile`) would require enumerating every profile in a domain, and
the object and profile size quotas bound a single record. Segment snapshots per
day is a rolling daily rate. None of these is measured here.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

PROFILES = 'customer-profiles'


def domains(ctx):
    found = []
    for item in ctx.call(PROFILES, 'list_domains', 'Items'):
        name = item.get('DomainName')
        if not isinstance(name, str) or not name:
            raise NoData('Customer Profiles domain is missing its name')
        if name not in found:
            found.append(name)
    return found


def _per_domain(method, key, resource='CustomerProfilesDomain'):
    """Report the largest inventory of one child resource across all domains."""
    def check(ctx):
        values = [(domain, len(ctx.call(PROFILES, method, key, DomainName=domain)), None)
                  for domain in domains(ctx)]
        source = f'customer-profiles:{_operation(method)}'
        return maximum(values, resource, source)
    return check


def _operation(method):
    return ''.join(part.capitalize() for part in method.split('_'))


def object_types(domain, ctx):
    found = []
    for item in ctx.call(PROFILES, 'list_profile_object_types', 'Items',
                         DomainName=domain):
        name = item.get('ObjectTypeName')
        if not isinstance(name, str) or not name:
            raise NoData('Customer Profiles object type is missing its name')
        found.append(name)
    return found


def keys_per_object_type(ctx):
    values = []
    for domain in domains(ctx):
        for name in object_types(domain, ctx):
            detail = ctx.call(PROFILES, 'get_profile_object_type',
                              DomainName=domain, ObjectTypeName=name)
            keys = detail.get('Keys')
            if keys is None:
                keys = {}
            if not isinstance(keys, dict):
                raise NoData('Customer Profiles object type has invalid keys')
            values.append((f'{domain}/{name}', len(keys), None))
    return maximum(values, 'CustomerProfilesObjectType',
                   'customer-profiles:GetProfileObjectType')


def expiration_days(ctx):
    """Report the longest retention configured on a domain or object type."""
    values = []
    for domain in domains(ctx):
        detail = ctx.call(PROFILES, 'get_domain', DomainName=domain)
        configured = [detail.get('DefaultExpirationDays')]
        for name in object_types(domain, ctx):
            object_type = ctx.call(PROFILES, 'get_profile_object_type',
                                   DomainName=domain, ObjectTypeName=name)
            configured.append(object_type.get('ExpirationDays'))
        days = [value for value in configured if isinstance(value, int)]
        values.append((domain, max(days, default=0), None))
    return maximum(values, 'CustomerProfilesDomain', 'customer-profiles:GetDomain')


CHECKS = [
    ('L-6603B252', 'Amazon Connect Customer Profiles domain count',
     lambda ctx: dict(usage=len(domains(ctx)),
                      source='customer-profiles:ListDomains',
                      method='ACCOUNT_COUNT')),
    ('L-14092FF4', 'Object types per domain',
     lambda ctx: maximum([(domain, len(object_types(domain, ctx)), None)
                          for domain in domains(ctx)], 'CustomerProfilesDomain',
                         'customer-profiles:ListProfileObjectTypes')),
    ('L-9CF9A111', 'Maximum number of domain object types per domain',
     _per_domain('list_domain_object_types', 'Items')),
    ('L-A7ED412C', 'Keys per object type', keys_per_object_type),
    ('L-3217D1F1', 'Maximum expiration in days', expiration_days),
    ('L-DB27F954', 'Maximum number of calculated attributes per domain',
     _per_domain('list_calculated_attribute_definitions', 'Items')),
    ('L-1DED0840', 'Maximum number of event stream per domain',
     _per_domain('list_event_streams', 'Items')),
    ('L-0A1E1791', 'Maximum number of event triggers per domain',
     _per_domain('list_event_triggers', 'Items')),
    ('L-4A5ECB8E', 'Maximum number of integrations',
     _per_domain('list_integrations', 'Items')),
    ('L-B6E9F054', 'Maximum number of recommenders per domain',
     _per_domain('list_recommenders', 'Recommenders')),
    ('L-ECB9B0BB', 'Maximum number of recommender schemas per domain',
     _per_domain('list_recommender_schemas', 'RecommenderSchemas')),
    ('L-D53B7246', 'Maximum number of recommeneder filters per domain',
     _per_domain('list_recommender_filters', 'RecommenderFilters')),
]


def get_current_quotastatus_customer_profiles(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'profile' for service, _ in context.quotas):
        return []
    return context.run('profile', CHECKS, skip)
