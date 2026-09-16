"""AWS Lake Formation regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call('lakeformation', method, key, **kwargs)),
                source=f'lakeformation:{method}', method='ACCOUNT_COUNT')


def administrators(ctx):
    settings = ctx.call('lakeformation', 'get_data_lake_settings')
    return dict(usage=len(settings.get('DataLakeSettings', {}).get('DataLakeAdmins', [])),
                source='lakeformation:GetDataLakeSettings', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-B0A837CA', 'Number of registered paths',
     lambda ctx: resource_count(ctx, 'list_resources', 'ResourceInfoList')),
    ('L-3E3798DF', 'Number of data lake administrators', administrators),
    ('L-F165AF61', 'Number of LF tags per account',
     lambda ctx: resource_count(ctx, 'list_lf_tags', 'LFTags')),
]


def get_current_quotastatus_lakeformation(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'lakeformation' for service, _ in context.quotas):
        return []
    return context.run('lakeformation', CHECKS, skip)
