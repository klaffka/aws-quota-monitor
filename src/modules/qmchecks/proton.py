"""AWS Proton regional resource and per-parent quota inventories."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


TEMPLATE_TYPES = {
    'environment': ('list_environment_templates', 'list_environment_template_versions'),
    'service': ('list_service_templates', 'list_service_template_versions'),
}


def _inventory(ctx, method, key, identity_field='arn', **kwargs):
    items = []
    identities = set()
    for item in ctx.call('proton', method, key, **kwargs):
        if not isinstance(item, dict):
            raise NoData(f'Proton {key} inventory contains an invalid item')
        identity = item.get(identity_field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'Proton {key} item is missing an identity')
        if identity in identities:
            raise NoData(f'Proton {key} inventory contains a duplicate')
        identities.add(identity)
        items.append(item)
    return items


def _templates(ctx, template_type):
    list_method, _ = TEMPLATE_TYPES[template_type]
    templates = _inventory(ctx, list_method, 'templates')
    for template in templates:
        if not isinstance(template.get('name'), str) or not template['name']:
            raise NoData('Proton template is missing its name')
    return templates


def template_count(ctx):
    count = sum(len(_templates(ctx, template_type)) for template_type in TEMPLATE_TYPES)
    return dict(usage=count,
                source='proton:ListEnvironmentTemplates+ListServiceTemplates',
                method='ACCOUNT_COUNT')


def component_count(ctx):
    components = _inventory(ctx, 'list_components', 'components')
    for component in components:
        if not isinstance(component.get('name'), str) or not component['name']:
            raise NoData('Proton component is missing its name')
    return dict(usage=len(components), source='proton:ListComponents',
                method='ACCOUNT_COUNT')


def environment_account_connections(ctx):
    connections = []
    identities = set()
    for requested_by in ('MANAGEMENT_ACCOUNT', 'ENVIRONMENT_ACCOUNT'):
        items = ctx.call('proton', 'list_environment_account_connections',
                         'environmentAccountConnections', requestedBy=requested_by)
        for item in items:
            if not isinstance(item, dict):
                raise NoData('Proton connection inventory contains an invalid item')
            identity = item.get('id')
            environment_account = item.get('environmentAccountId')
            management_account = item.get('managementAccountId')
            if (not isinstance(identity, str) or not identity
                    or not isinstance(environment_account, str) or not environment_account
                    or not isinstance(management_account, str) or not management_account):
                raise NoData('Proton connection is missing required identity data')
            expected_account = (management_account if requested_by == 'MANAGEMENT_ACCOUNT'
                                else environment_account)
            if expected_account != ctx.account:
                raise NoData('Proton connection inventory has an inconsistent account scope')
            if identity in identities:
                raise NoData('Proton connection inventory contains a duplicate')
            identities.add(identity)
            connections.append((environment_account, identity))
    return connections


def connections_per_environment_account(ctx):
    counts = Counter(account for account, _ in environment_account_connections(ctx))
    return maximum(((account, count, None) for account, count in counts.items()),
                   'ProtonEnvironmentAccount',
                   'proton:ListEnvironmentAccountConnections')


def _versions_for_template(ctx, template_type, template_name):
    _, version_method = TEMPLATE_TYPES[template_type]
    major_summaries = _inventory(
        ctx, version_method, 'templateVersions', templateName=template_name)
    major_versions = set()
    for version in major_summaries:
        major = version.get('majorVersion')
        if (version.get('templateName') != template_name
                or not isinstance(major, str) or not major):
            raise NoData('Proton template-version inventory has an inconsistent parent')
        if major in major_versions:
            raise NoData('Proton template-version inventory contains a duplicate major version')
        major_versions.add(major)

    versions = set()
    for major in major_versions:
        minor_versions = _inventory(
            ctx, version_method, 'templateVersions', templateName=template_name,
            majorVersion=major)
        for version in minor_versions:
            minor = version.get('minorVersion')
            if (version.get('templateName') != template_name
                    or version.get('majorVersion') != major
                    or not isinstance(minor, str) or not minor):
                raise NoData('Proton template-version inventory has an inconsistent parent')
            identity = (major, minor)
            if identity in versions:
                raise NoData('Proton template-version inventory contains a duplicate version')
            versions.add(identity)
    return versions


def template_versions_per_template(ctx):
    values = []
    for template_type in TEMPLATE_TYPES:
        for template in _templates(ctx, template_type):
            name = template['name']
            count = len(_versions_for_template(ctx, template_type, name))
            values.append((f'{template_type}:{name}', count, None))
    return maximum(values, 'ProtonTemplate',
                   'proton:ListEnvironmentTemplateVersions+ListServiceTemplateVersions')


def service_instances_per_service(ctx):
    instances = _inventory(ctx, 'list_service_instances', 'serviceInstances')
    counts = Counter()
    for instance in instances:
        service_name = instance.get('serviceName')
        name = instance.get('name')
        if (not isinstance(service_name, str) or not service_name
                or not isinstance(name, str) or not name):
            raise NoData('Proton service instance is missing its parent identity')
        counts[service_name] += 1
    return maximum(((service, count, None) for service, count in counts.items()),
                   'ProtonService', 'proton:ListServiceInstances')


CHECKS = [
    ('L-1C8983C3', 'Services per account',
     lambda c: dict(usage=len(c.call('proton', 'list_services', 'services')),
                    source='proton:ListServices', method='ACCOUNT_COUNT')),
    ('L-37A692EA', 'Environments per account',
     lambda c: dict(usage=len(c.call('proton', 'list_environments', 'environments')),
                    source='proton:ListEnvironments', method='ACCOUNT_COUNT')),
    ('L-405DC02B', 'Templates per account', template_count),
    ('L-6CC8209C', 'Environment account connections per environment account',
     connections_per_environment_account),
    ('L-8FBB60E3', 'Components per account', component_count),
    ('L-A1B6A95A', 'Template versions per template', template_versions_per_template),
    ('L-E8182F7E', 'Service instances per service', service_instances_per_service),
]


def get_current_quotastatus_proton(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'proton' for service, _ in context.quotas):
        return []
    return context.run('proton', CHECKS, skip)
