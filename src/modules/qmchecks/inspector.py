"""Amazon Inspector regional suppression-rule quota."""
from modules.qmcore.aws import CheckContext, session_from_env


def suppression_rules(ctx):
    return [item for item in ctx.call('inspector2', 'list_filters', 'filters')
            if item.get('action') == 'SUPPRESS']


CHECKS = [
    ('L-3CFEE10A', 'Number of Suppression Rules',
     lambda ctx: dict(usage=len(suppression_rules(ctx)), source='inspector2:ListFilters',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_inspector(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'inspector2' for service, _ in context.quotas):
        return []
    return context.run('inspector2', CHECKS, skip)
