"""Route 53 Profiles regional profile counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [('L-D9B2356C', 'Route 53 Profiles per account per Region',
           lambda c: dict(usage=len(c.call('route53profiles', 'list_profiles', 'ProfileSummaries')),
                          source='route53profiles:ListProfiles', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_route53profiles(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'route53profiles' for service, _ in context.quotas): return []
    return context.run('route53profiles', CHECKS, skip)
