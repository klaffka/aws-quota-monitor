"""Amazon EventBridge Schemas registry, schema and discoverer quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SCHEMAS = 'schemas'
DISCOVERED_REGISTRY = 'discovered-schemas'


def registries(ctx):
    found = []
    for registry in ctx.call(SCHEMAS, 'list_registries', 'Registries'):
        name = registry.get('RegistryName')
        if not isinstance(name, str) or not name:
            raise NoData('Schema registry is missing its name')
        if name not in found:
            found.append(name)
    return found


def schemas_in(registry, ctx):
    found = {}
    for schema in ctx.call(SCHEMAS, 'list_schemas', 'Schemas', RegistryName=registry):
        name = schema.get('SchemaName')
        if not isinstance(name, str) or not name:
            raise NoData('Schema is missing its name')
        found[name] = schema
    return found


def schemas_per_registry(ctx):
    values = [(registry, len(schemas_in(registry, ctx)), None)
              for registry in registries(ctx)]
    return maximum(values, 'SchemaRegistry', 'schemas:ListSchemas')


def discovered_schemas(ctx):
    """Count the schemas EventBridge discovered, which share one registry."""
    if DISCOVERED_REGISTRY not in registries(ctx):
        return dict(usage=0, source='schemas:ListSchemas', method='ACCOUNT_COUNT')
    return dict(usage=len(schemas_in(DISCOVERED_REGISTRY, ctx)),
                source='schemas:ListSchemas', method='ACCOUNT_COUNT')


def versions_per_schema(ctx):
    """Use the version counter AWS reports on each schema summary."""
    values = []
    for registry in registries(ctx):
        for name, schema in schemas_in(registry, ctx).items():
            count = schema.get('VersionCount')
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise NoData('Schema has no version count')
            values.append((f'{registry}/{name}', count, None))
    return maximum(values, 'Schema', 'schemas:ListSchemas')


CHECKS = [
    ('L-85663EFB', 'Registries',
     lambda ctx: dict(usage=len(registries(ctx)), source='schemas:ListRegistries',
                      method='ACCOUNT_COUNT')),
    ('L-EE9E5FA9', 'Schemas', schemas_per_registry),
    ('L-3C443A2A', 'SchemaVersions', versions_per_schema),
    ('L-1738102F', 'DiscoveredSchemas', discovered_schemas),
    ('L-037FC7C4', 'Discoverers',
     lambda ctx: dict(usage=len(ctx.call(SCHEMAS, 'list_discoverers', 'Discoverers')),
                      source='schemas:ListDiscoverers', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_schemas(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'schemas' for service, _ in context.quotas):
        return []
    return context.run('schemas', CHECKS, skip)
