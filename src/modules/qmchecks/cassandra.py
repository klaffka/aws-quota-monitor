"""Amazon Keyspaces (for Apache Cassandra) keyspace, table and type quotas.

The catalog calls the service `cassandra`, but the SDK client is `keyspaces`,
and every table and type listing is scoped to one keyspace.

The table-level throughput quotas read as rates but bound provisioned capacity,
which the table stores: one in on-demand mode provisions nothing, which is zero
rather than absent.
"""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

KEYSPACES = 'keyspaces'
# AWS's own keyspaces, listed beside the account's. Nobody can create or drop
# them, they count towards no quota, and GetTable does not answer for them.
SYSTEM_KEYSPACES = {'system', 'system_schema', 'system_schema_mcs', 'system_multiregion_info'}


def keyspaces(ctx):
    found = []
    for keyspace in ctx.call(KEYSPACES, 'list_keyspaces', 'keyspaces'):
        name = keyspace.get('keyspaceName')
        if not isinstance(name, str) or not name:
            raise NoData('Keyspaces keyspace is missing its name')
        if name not in SYSTEM_KEYSPACES:
            found.append(name)
    return found


def tables(ctx):
    found = []
    for keyspace in keyspaces(ctx):
        for table in ctx.call(KEYSPACES, 'list_tables', 'tables',
                              keyspaceName=keyspace):
            name = table.get('tableName')
            if not isinstance(name, str) or not name:
                raise NoData('Keyspaces table is missing its name')
            found.append(f'{keyspace}.{name}')
    return found


def table_capacity(field):
    """The listing carries no capacity, so each table is fetched for it."""
    def check(ctx):
        values = []
        for keyspace in keyspaces(ctx):
            for table in ctx.call(KEYSPACES, 'list_tables', 'tables',
                                  keyspaceName=keyspace):
                name = table.get('tableName')
                if not isinstance(name, str) or not name:
                    raise NoData('Keyspaces table is missing its name')
                detail = ctx.call(KEYSPACES, 'get_table', keyspaceName=keyspace,
                                  tableName=name)
                if (detail.get('keyspaceName'), detail.get('tableName')) != (keyspace, name):
                    raise NoData('Keyspaces table does not match the requested identity')
                capacity = detail.get('capacitySpecification') or {}
                values.append((f'{keyspace}.{name}', capacity.get(field) or 0, None))
        return maximum(values, 'KeyspacesTable', 'keyspaces:GetTable')
    return check


def types(ctx):
    """Describe every user-defined type; the listing returns names alone."""
    found = {}
    for keyspace in keyspaces(ctx):
        for name in ctx.call(KEYSPACES, 'list_types', 'types',
                             keyspaceName=keyspace):
            if not isinstance(name, str) or not name:
                raise NoData('Keyspaces type is missing its name')
            detail = ctx.call(KEYSPACES, 'get_type', keyspaceName=keyspace,
                              typeName=name)
            if (detail.get('keyspaceName'), detail.get('typeName')) != (keyspace, name):
                raise NoData('Keyspaces type does not match the requested identity')
            found[f'{keyspace}.{name}'] = detail
    return found


def _references(detail, field, subject):
    entries = detail.get(field)
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise NoData(f'Keyspaces type has an invalid {subject} list')
    return entries


def tables_per_type(ctx):
    values = [(identity, len(_references(detail, 'directReferringTables', 'table')), None)
              for identity, detail in types(ctx).items()]
    return maximum(values, 'KeyspacesType', 'keyspaces:GetType')


def types_per_table(ctx):
    counts = Counter()
    for detail in types(ctx).values():
        keyspace = detail['keyspaceName']
        for table in _references(detail, 'directReferringTables', 'table'):
            counts[f'{keyspace}.{table}'] += 1
    return maximum(((table, count, None) for table, count in counts.items()),
                   'KeyspacesTable', 'keyspaces:GetType')


def parent_types_per_type(ctx):
    values = [(identity, len(_references(detail, 'directParentTypes', 'parent type')),
               None)
              for identity, detail in types(ctx).items()]
    return maximum(values, 'KeyspacesType', 'keyspaces:GetType')


def child_types_per_type(ctx):
    """A child names its parents, so the child count is the reverse mapping."""
    counts = Counter()
    for detail in types(ctx).values():
        keyspace = detail['keyspaceName']
        for parent in _references(detail, 'directParentTypes', 'parent type'):
            counts[f'{keyspace}.{parent}'] += 1
    return maximum(((identity, count, None) for identity, count in counts.items()),
                   'KeyspacesType', 'keyspaces:GetType')


def longest_type_name(ctx):
    values = [(identity, len(detail['typeName']), None)
              for identity, detail in types(ctx).items()]
    return maximum(values, 'KeyspacesType', 'keyspaces:ListTypes')


CHECKS = [
    ('L-677FFD22', 'Keyspaces per region',
     lambda ctx: dict(usage=len(keyspaces(ctx)), source='keyspaces:ListKeyspaces',
                      method='ACCOUNT_COUNT')),
    ('L-BF48748A', 'Tables per region',
     lambda ctx: dict(usage=len(tables(ctx)),
                      source='keyspaces:ListKeyspaces+ListTables',
                      method='ACCOUNT_COUNT')),
    ('L-7A88D508', 'Max number of UDTs per AWS Region',
     lambda ctx: dict(usage=len(types(ctx)),
                      source='keyspaces:ListKeyspaces+ListTypes',
                      method='ACCOUNT_COUNT')),
    ('L-089904FB', 'Max number of tables per UDT', tables_per_type),
    ('L-96FEFC6D', 'Max number of UDTs per table', types_per_table),
    ('L-C63C913D', 'Max amount of direct parent UDTs per UDT', parent_types_per_type),
    ('L-F90953AC', 'Max amount of direct child UDTs per UDT', child_types_per_type),
    ('L-964C49BD', 'Max UDT name length', longest_type_name),
    ('L-17766544', 'Table-level read throughput quota',
     table_capacity('readCapacityUnits')),
    ('L-3D8ED127', 'Table-level write throughput quota',
     table_capacity('writeCapacityUnits')),
]


def get_current_quotastatus_cassandra(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cassandra' for service, _ in context.quotas):
        return []
    return context.run('cassandra', CHECKS, skip)
