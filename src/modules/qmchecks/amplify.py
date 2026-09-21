"""AWS Amplify app, domain and subdomain inventory."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

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


def subdomains_per_domain(ctx):
    """The quota is per domain, so the maximum runs over domains, not apps."""
    values = []
    for app in ctx.call('amplify', 'list_apps', 'apps'):
        app_id = app.get('appId')
        if not app_id:
            continue
        for domain in ctx.call('amplify', 'list_domain_associations',
                               'domainAssociations', appId=app_id):
            name = domain.get('domainName')
            if not isinstance(name, str) or not name:
                raise NoData('Amplify domain association is missing its name')
            values.append((f'{app_id}/{name}',
                           len(domain.get('subDomains') or ()), None))
    return maximum(values, 'AmplifyDomain', 'amplify:ListDomainAssociations')


CHECKS = [('L-1BED97F3', 'Apps',
           lambda ctx: dict(usage=len(ctx.call('amplify', 'list_apps', 'apps')),
                            source='amplify:ListApps', method='ACCOUNT_COUNT')),
          ('L-AD277529', 'Domains per app', domains_per_app)]
CHECKS.extend([
    ('L-A6716586', 'Branches per app',
     lambda ctx: children_per_app(ctx, 'list_branches', 'branches')),
    ('L-4113FC04', 'Webhooks per app',
     lambda ctx: children_per_app(ctx, 'list_webhooks', 'webhooks')),
    ('L-85685B2E', 'Subdomains per domain', subdomains_per_domain),
])


def get_current_quotastatus_amplify(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'amplify' for service, _ in context.quotas): return []
    return context.run('amplify', CHECKS, skip)
