"""IAM Roles Anywhere regional resource counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-950ED79F', 'Profiles',
     lambda c: dict(usage=len(c.call('rolesanywhere', 'list_profiles', 'profiles')),
                    source='rolesanywhere:ListProfiles', method='ACCOUNT_COUNT')),
    ('L-AB49EEA7', 'Trust anchors',
     lambda c: dict(usage=len(c.call('rolesanywhere', 'list_trust_anchors', 'trustAnchors')),
                    source='rolesanywhere:ListTrustAnchors', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_rolesanywhere(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'rolesanywhere' for service, _ in context.quotas):
        return []
    return context.run('rolesanywhere', CHECKS, skip)
