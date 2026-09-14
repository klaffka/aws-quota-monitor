"""AWS Amplify app inventory."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env

def domains_per_app(ctx):
    values = []
    for app in ctx.call('amplify', 'list_apps', 'apps'):
        app_id = app.get('appId')
        if app_id:
            values.append((app_id, len(ctx.call('amplify', 'list_domain_associations', 'domainAssociations', appId=app_id)), None))
    return maximum(values, 'AmplifyApp', 'amplify:ListApps+ListDomainAssociations')


def children_per_app(ctx, method, key):
    values = []
    for app in ctx.call('amplify', 'list_apps', 'apps'):
        app_id = app.get('appId')
        if app_id:
            values.append((app_id, len(ctx.call('amplify', method, key, appId=app_id)), None))
    return maximum(values, 'AmplifyApp', f'amplify:{method}')


CHECKS = [('L-1BED97F3', 'Apps',
           lambda ctx: dict(usage=len(ctx.call('amplify', 'list_apps', 'apps')),
                            source='amplify:ListApps', method='ACCOUNT_COUNT')),
          ('L-AD277529', 'Domains per app', domains_per_app)]
CHECKS.extend([
    ('L-A6716586', 'Branches per app',
     lambda ctx: children_per_app(ctx, 'list_branches', 'branches')),
    ('L-4113FC04', 'Webhooks per app',
     lambda ctx: children_per_app(ctx, 'list_webhooks', 'webhooks')),
])


def get_current_quotastatus_amplify(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'amplify' for service, _ in context.quotas): return []
    return context.run('amplify', CHECKS, skip)
