"""DynamoDB regional table and secondary index inventory.

`Concurrent control plane operations` and the incremental export quotas count
work in flight or name a period, so neither is an inventory.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DYNAMODB = 'dynamodb'


def tables(ctx):
    return ctx.call(DYNAMODB, 'list_tables', 'TableNames')


def secondary_indexes_per_table(ctx):
    """A table holding no secondary index counts as zero rather than dropping out."""
    values = []
    for name in tables(ctx):
        if not isinstance(name, str) or not name:
            raise NoData('DynamoDB table is missing its name')
        table = ctx.call(DYNAMODB, 'describe_table', TableName=name).get('Table') or {}
        indexes = table.get('GlobalSecondaryIndexes') or []
        if not isinstance(indexes, list):
            raise NoData('DynamoDB table has an invalid secondary index list')
        values.append((name, len(indexes), None))
    return maximum(values, 'DynamoDBTable', 'dynamodb:DescribeTable')


CHECKS = [
    ('L-F98FE922', 'Maximum number of tables',
     lambda ctx: dict(usage=len(tables(ctx)), source='dynamodb:ListTables',
                      method='ACCOUNT_COUNT')),
    ('L-F7858A77', 'Global Secondary Indexes per table', secondary_indexes_per_table),
]


def get_current_quotastatus_dynamodb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dynamodb' for service, _ in context.quotas):
        return []
    return context.run('dynamodb', CHECKS, skip)
