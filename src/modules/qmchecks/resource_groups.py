"""AWS Resource Groups regional resource-count quota."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-2BAA18A0', 'Resource groups per account',
     lambda ctx: dict(usage=len(ctx.call('resource-groups', 'list_groups', 'Groups')),
                      source='resource-groups:ListGroups', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_resource_groups(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'resource-groups' for service, _ in context.quotas):
        return []
    return context.run('resource-groups', CHECKS, skip)
