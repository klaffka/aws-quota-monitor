"""Amazon DataZone domain-scoped resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def domains(ctx):
    return ctx.call('datazone', 'list_domains', 'items')


def maximum_per_domain(ctx, method, key):
    values = []
    for domain in domains(ctx):
        identifier = domain.get('id') or domain.get('domainId')
        items = ctx.call('datazone', method, key, domainIdentifier=identifier)
        values.append((identifier, len(items), None))
    return maximum(values, 'DataZoneDomain', f'datazone:{method}')


def git_connections_per_project(ctx):
    values = []
    for domain in domains(ctx):
        domain_id = domain.get('id') or domain.get('domainId')
        if not domain_id:
            continue
        for project in ctx.call('datazone', 'list_projects', 'items', domainIdentifier=domain_id):
            project_id = project.get('id') or project.get('projectId')
            if project_id:
                values.append((project_id, len(ctx.call('datazone', 'list_connections', 'items',
                                                        projectIdentifier=project_id, type='GIT')), None))
    return maximum(values, 'DataZoneProject', 'datazone:ListConnections(type=GIT)')


CHECKS = [
    ('L-06335BC6', 'Assets', lambda ctx: maximum_per_domain(ctx, 'list_assets', 'items')),
    ('L-2C2845D2', 'Glossaries', lambda ctx: maximum_per_domain(ctx, 'list_glossaries', 'items')),
    ('L-9EF33583', 'Asset Types', lambda ctx: maximum_per_domain(ctx, 'list_asset_types', 'items')),
    ('L-EDF6298B', 'Environments in a domain',
     lambda ctx: maximum_per_domain(ctx, 'list_environments', 'items')),
    ('L-FAD0E7F7', 'Git connections per project', git_connections_per_project),
]


def get_current_quotastatus_datazone(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'datazone' for service, _ in context.quotas): return []
    return context.run('datazone', CHECKS, skip)
