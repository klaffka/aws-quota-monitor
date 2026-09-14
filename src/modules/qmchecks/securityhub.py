"""AWS Security Hub regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('securityhub', method, key)),
                source=f'securityhub:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-D348B3A2', 'Automation rules',
     lambda ctx: resource_count(ctx, 'list_automation_rules', 'AutomationRulesMetadata')),
    ('L-D639633A', 'Custom actions',
     lambda ctx: resource_count(ctx, 'describe_action_targets', 'ActionTargets')),
    ('L-1AA69D21', 'Custom insights',
     lambda ctx: resource_count(ctx, 'get_insights', 'Insights')),
    ('L-6E4302A5', 'Security Hub member accounts',
     lambda ctx: resource_count(ctx, 'get_members', 'Members')),
    ('L-387C829B', 'Security Hub outstanding invitations',
     lambda ctx: dict(usage=ctx.call('securityhub', 'get_invitations_count').get('InvitationsCount', 0),
                      source='securityhub:GetInvitationsCount', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_securityhub(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'securityhub' for service, _ in context.quotas):
        return []
    return context.run('securityhub', CHECKS, skip)
