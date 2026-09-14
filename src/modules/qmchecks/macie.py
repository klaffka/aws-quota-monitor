"""Amazon Macie regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('macie2', method, key)),
                source=f'macie2:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-7D690B48', 'Custom data identifiers per account',
     lambda ctx: resource_count(ctx, 'list_custom_data_identifiers', 'items')),
    ('L-E2FBEE6E', 'Findings rules',
     lambda ctx: resource_count(ctx, 'list_findings_filters', 'findingsFilterListItems')),
    ('L-2F634A96', 'Member accounts through AWS Organizations',
     lambda ctx: resource_count(ctx, 'list_members', 'members')),
    ('L-7AF7F5C8', 'Member accounts by invitation',
     lambda ctx: dict(usage=ctx.call('macie2', 'get_invitations_count').get('invitationsCount', 0),
                      source='macie2:GetInvitationsCount', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_macie(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'macie2' for service, _ in context.quotas):
        return []
    return context.run('macie2', CHECKS, skip)
