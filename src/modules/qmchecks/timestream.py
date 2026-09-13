"""Amazon Timestream regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def databases(ctx):
    return ctx.call('timestream-write', 'list_databases', 'Databases')


def tables_per_database(ctx):
    values = []
    for database in databases(ctx):
        name = database.get('DatabaseName')
        tables = ctx.call('timestream-write', 'list_tables', 'Tables', DatabaseName=name)
        values.append((name, len(tables), None))
    return maximum(values, 'TimestreamDatabase', 'timestream-write:ListTables')


def total_tables(ctx):
    usage = 0
    for database in databases(ctx):
        usage += len(ctx.call('timestream-write', 'list_tables', 'Tables',
                              DatabaseName=database.get('DatabaseName')))
    return dict(usage=usage, source='timestream-write:ListTables', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-FD5A0C1A', 'Databases per account',
     lambda ctx: dict(usage=len(databases(ctx)), source='timestream-write:ListDatabases', method='ACCOUNT_COUNT')),
    ('L-1222731D', 'Tables per account',
     total_tables),
    ('L-F1AC16A2', 'Scheduled queries per account',
     lambda ctx: dict(usage=len(ctx.call('timestream-query', 'list_scheduled_queries', 'ScheduledQueries')),
                      source='timestream-query:ListScheduledQueries', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_timestream(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'timestream' for service, _ in context.quotas):
        return []
    return context.run('timestream', CHECKS, skip)
