"""AWS Support authorization permit quota."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

SUPPORT_AUTHZ = 'supportauthz'


def support_permits(ctx):
    found = set()
    for permit in ctx.call(SUPPORT_AUTHZ, 'list_support_permits', 'supportPermits'):
        arn = permit.get('arn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Support permit is missing its ARN')
        found.add(arn)
    return dict(usage=len(found), source='supportauthz:ListSupportPermits',
                method='ACCOUNT_COUNT')


CHECKS = [('L-EDDA9F00', 'Support permits per account', support_permits)]


def get_current_quotastatus_supportauthz(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'supportauthz' for service, _ in context.quotas):
        return []
    return context.run('supportauthz', CHECKS, skip)
