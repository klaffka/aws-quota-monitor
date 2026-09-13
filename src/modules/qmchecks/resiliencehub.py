"""AWS Resilience Hub regional application resource quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key, **kwargs):
    return dict(usage=len(ctx.call('resiliencehub', method, key, **kwargs)),
                source=f'resiliencehub:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-CBE304D4', 'Number of applications',
     lambda ctx: resource_count(ctx, 'list_apps', 'appSummaries')),
    ('L-F9AC239A', 'Number of Resiliency Policies',
     lambda ctx: resource_count(ctx, 'list_resiliency_policies', 'resiliencyPolicies')),
]


def get_current_quotastatus_resiliencehub(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'resiliencehub' for service, _ in context.quotas):
        return []
    return context.run('resiliencehub', CHECKS, skip)
