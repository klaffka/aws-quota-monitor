"""Amplify UI Builder per-app resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def per_app(ctx, method, key):
    values = []
    for app in ctx.call('amplify', 'list_apps', 'apps'):
        app_id = app.get('appId')
        if app_id:
            values.append((app_id, len(ctx.call('amplifyuibuilder', method, key, appId=app_id)), None))
    return maximum(values, 'AmplifyApp', f'amplifyuibuilder:{method}')


CHECKS = [
    ('L-429DD3BA', 'Themes per app', lambda c: per_app(c, 'list_themes', 'themes')),
    ('L-E4AD9560', 'Views per app', lambda c: per_app(c, 'list_views', 'views')),
    ('L-E5E3CF14', 'Components per app', lambda c: per_app(c, 'list_components', 'components')),
    ('L-F527F6EB', 'Forms per app', lambda c: per_app(c, 'list_forms', 'forms')),
]


def get_current_quotastatus_amplifyuibuilder(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'amplifyuibuilder' for service, _ in context.quotas):
        return []
    return context.run('amplifyuibuilder', CHECKS, skip)
