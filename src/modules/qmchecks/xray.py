"""AWS X-Ray regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('xray', method, key)),
                source=f'xray:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-7F259013', 'Groups in an account',
     lambda ctx: resource_count(ctx, 'get_groups', 'Groups')),
    ('L-8C0C998A', 'Custom sampling rules per region',
     lambda ctx: resource_count(ctx, 'get_sampling_rules', 'SamplingRuleRecords')),
]


def get_current_quotastatus_xray(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'xray' for service, _ in context.quotas):
        return []
    return context.run('xray', CHECKS, skip)
