"""Amazon Cognito regional user-pool inventory."""
from modules.qmcore.aws import CheckContext, session_from_env

# ListUserPools requires a page size; 60 is the documented maximum.
PAGE_SIZE = 60

CHECKS = [
    ('L-66E6DF30', 'User pools per account',
     lambda ctx: dict(usage=len(ctx.call('cognito-idp', 'list_user_pools', 'UserPools', MaxResults=PAGE_SIZE)),
                      source='cognito-idp:ListUserPools', method='ACCOUNT_COUNT')),
    ('L-71267F98', 'Custom domains per account',
     lambda ctx: dict(usage=sum(bool(ctx.call('cognito-idp', 'describe_user_pool', UserPoolId=p['Id'])['UserPool'].get('CustomDomain'))
                                  for p in ctx.call('cognito-idp', 'list_user_pools', 'UserPools', MaxResults=PAGE_SIZE)),
                      source='cognito-idp:ListUserPools+DescribeUserPool', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_cognito(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cognito-idp' for service, _ in context.quotas):
        return []
    return context.run('cognito-idp', CHECKS, skip)
