"""DynamoDB regional table inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-F98FE922', 'Maximum number of tables',
           lambda ctx: dict(usage=len(ctx.call('dynamodb', 'list_tables', 'TableNames')),
                            source='dynamodb:ListTables', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_dynamodb(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'dynamodb' for service, _ in context.quotas): return []
    return context.run('dynamodb', CHECKS, skip)
