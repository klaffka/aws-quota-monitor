"""AWS RAM resource-share counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-595828F9', 'Number of resource shares',
     lambda c: dict(usage=len(c.call('ram', 'get_resource_shares', 'resourceShares', resourceOwner='SELF')),
                    source='ram:GetResourceShares', method='ACCOUNT_COUNT')),
    ('L-8491BF81', 'Number of principal associations',
     lambda c: dict(usage=len(c.call('ram', 'list_principals', 'principals', resourceOwner='SELF')),
                    source='ram:ListPrincipals', method='ACCOUNT_COUNT')),
    ('L-238C96EE', 'Number of pending invitations',
     lambda c: dict(usage=len(c.call('ram', 'get_resource_share_invitations',
                                    'resourceShareInvitations')),
                    source='ram:GetResourceShareInvitations', method='ACCOUNT_COUNT')),
]

def get_current_quotastatus_ram(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ram' for service, _ in context.quotas): return []
    return context.run('ram', CHECKS, skip)
