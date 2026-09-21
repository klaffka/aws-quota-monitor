"""AWS Mainframe Modernization resource and environment storage inventories.

`Max DataTransferEndpoints Per AWS Account` is left open: this SDK ships no
listing for data transfer endpoints under any name.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

M2 = 'm2'


def count(ctx, method, key):
    return dict(usage=len(ctx.call(M2, method, key)), source=f'm2:{method}',
                method='ACCOUNT_COUNT')


def _filesystems(kind):
    """Count the mounts of one kind; a storage configuration names exactly one."""
    def check(ctx):
        values = []
        for summary in ctx.call(M2, 'list_environments', 'environments'):
            identity = summary.get('environmentId')
            if not isinstance(identity, str) or not identity:
                raise NoData('Mainframe Modernization environment is missing its identity')
            detail = ctx.call(M2, 'get_environment', environmentId=identity)
            storage = detail.get('storageConfigurations') or []
            if not isinstance(storage, list):
                raise NoData('Mainframe Modernization environment has invalid storage')
            values.append((identity, sum(kind in entry for entry in storage), None))
        return maximum(values, 'MainframeEnvironment', 'm2:GetEnvironment')
    return check


CHECKS = [
    ('L-00464274', 'Max Applications Per AWS Account',
     lambda ctx: count(ctx, 'list_applications', 'applications')),
    ('L-6851C542', 'Max Environments Per AWS Account',
     lambda ctx: count(ctx, 'list_environments', 'environments')),
    ('L-5D943D0B', 'Max number of EFS filesystems per environment', _filesystems('efs')),
    ('L-C1C41257', 'Max number of FSX filesystems per environment', _filesystems('fsx')),
]


def get_current_quotastatus_m2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'm2' for service, _ in context.quotas):
        return []
    return context.run('m2', CHECKS, skip)
