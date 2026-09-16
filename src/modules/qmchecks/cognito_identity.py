"""Amazon Cognito Identity regional identity-pool counts."""
from modules.qmcore.aws import CheckContext, session_from_env

# ListIdentityPools requires a page size; 60 is the documented maximum.
PAGE_SIZE = 60

CHECKS = [('L-8692CE1C', 'Identity pools per account',
           lambda c: dict(usage=len(c.call('cognito-identity', 'list_identity_pools', 'IdentityPools',
                                          MaxResults=PAGE_SIZE)),
                          source='cognito-identity:ListIdentityPools', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_cognito_identity(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cognito-identity' for service, _ in context.quotas): return []
    return context.run('cognito-identity', CHECKS, skip)
