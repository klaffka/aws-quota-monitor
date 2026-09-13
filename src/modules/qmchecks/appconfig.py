"""AWS AppConfig regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

def maximum_per_application(ctx, method):
    values=[]
    for app in applications(ctx):
        items=ctx.call('appconfig', method, 'Items', ApplicationId=app['Id'])
        values.append((app['Id'],len(items),None))
    return maximum(values,'AppConfigApplication',f'appconfig:{method}')

def applications(ctx):
    return ctx.call('appconfig','list_applications','Items')


def resource_count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call('appconfig', method, key, **kwargs)), source=f'appconfig:{method}', method='ACCOUNT_COUNT')


def per_application(ctx, method, key):
    apps = ctx.call('appconfig', 'list_applications', 'Items')
    values = []
    for app in apps:
        app_id = app.get('Id')
        items = ctx.call('appconfig', method, key, ApplicationId=app_id)
        values.append((app_id, len(items), None))
    return maximum(values, 'AppConfigApplication', f'appconfig:{method}')


CHECKS = [
    ('L-EEB0151E', 'Maximum number of applications', lambda ctx: resource_count(ctx, 'list_applications', 'Items')),
    ('L-F59D302B', 'Maximum number of deployment strategies',
     lambda ctx: resource_count(ctx, 'list_deployment_strategies', 'Items')),
    ('L-FA210A1F', 'Maximum number of configuration profiles per application',
     lambda ctx: per_application(ctx, 'list_configuration_profiles', 'Items')),
    ('L-A52E46BE', 'Maximum number of environments per application',
     lambda ctx: per_application(ctx, 'list_environments', 'Items')),
]


def get_current_quotastatus_appconfig(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appconfig' for service, _ in context.quotas):
        return []
    return context.run('appconfig', CHECKS, skip)
