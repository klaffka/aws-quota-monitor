"""Amplify UI Builder per-app resource inventories.

UI Builder scopes every entity to an app *and* one of the app's backend
environments, so the inventory is read per pair and reported as the largest
pair. ``Views per app`` has no listing operation and is left to the audit.
"""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def app_environments(ctx):
    """Yield every (app, backend environment) pair the account exposes."""
    for app in ctx.call('amplify', 'list_apps', 'apps'):
        app_id = app.get('appId')
        if not app_id:
            continue
        for environment in ctx.call('amplify', 'list_backend_environments',
                                    'backendEnvironments', appId=app_id):
            name = environment.get('environmentName')
            if name:
                yield app_id, name


def per_app(ctx, method):
    values = []
    for app_id, environment in app_environments(ctx):
        entities = ctx.call('amplifyuibuilder', method, 'entities',
                            appId=app_id, environmentName=environment)
        values.append((f'{app_id}/{environment}', len(entities), None))
    return maximum(values, 'AmplifyAppEnvironment', f'amplifyuibuilder:{method}')


CHECKS = [
    ('L-429DD3BA', 'Themes per app', lambda c: per_app(c, 'list_themes')),
    ('L-E5E3CF14', 'Components per app', lambda c: per_app(c, 'list_components')),
    ('L-F527F6EB', 'Forms per app', lambda c: per_app(c, 'list_forms')),
]


def get_current_quotastatus_amplifyuibuilder(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'amplifyuibuilder' for service, _ in context.quotas):
        return []
    return context.run('amplifyuibuilder', CHECKS, skip)
