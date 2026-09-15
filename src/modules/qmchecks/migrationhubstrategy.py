"""AWS Migration Hub Strategy Recommendations import and server quotas.

`Assessment Maximum` and `Active Assessment Maximum` count assessments, but the
API exposes only the current one through `GetAssessment` and never lists them.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

STRATEGY = 'migrationhubstrategy'
IMPORT_STATES = {'ImportInProgress', 'ImportFailed', 'ImportPartialSuccess',
                 'ImportSuccess', 'DeleteInProgress', 'DeleteFailed',
                 'DeletePartialSuccess', 'DeleteSuccess'}
RUNNING_STATES = {'ImportInProgress', 'DeleteInProgress'}


def active_imports(ctx):
    usage = 0
    for task in ctx.call(STRATEGY, 'list_import_file_task', 'taskInfos'):
        status = task.get('status')
        if status not in IMPORT_STATES:
            raise NoData('Migration import task has an unknown status')
        usage += status in RUNNING_STATES
    return dict(usage=usage, source='migrationhubstrategy:ListImportFileTask',
                method='ACCOUNT_COUNT')


def servers_per_assessment(ctx):
    """The server inventory belongs to the account's current assessment."""
    found = set()
    for server in ctx.call(STRATEGY, 'list_servers', 'serverInfos'):
        identity = server.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Migration server is missing its identity')
        found.add(identity)
    return dict(usage=len(found), source='migrationhubstrategy:ListServers',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-33C4B34A', 'Active Import Maximum', active_imports),
    ('L-649F667C', 'Maximum Server per Assessment', servers_per_assessment),
]


def get_current_quotastatus_migrationhubstrategy(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'migrationhubstrategy' for service, _ in context.quotas):
        return []
    return context.run('migrationhubstrategy', CHECKS, skip)
