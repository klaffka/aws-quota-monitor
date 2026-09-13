"""EC2 Image Builder regional lifecycle-policy counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-6105A4EE', 'Lifecycle policies',
     lambda c: dict(usage=len(c.call('imagebuilder', 'list_lifecycle_policies',
                                      'lifecyclePolicySummaryList')),
                    source='imagebuilder:ListLifecyclePolicies', method='ACCOUNT_COUNT')),
    ('L-9B183655', 'Components',
     lambda c: dict(usage=len(c.call('imagebuilder', 'list_components', 'componentVersionList')),
                    source='imagebuilder:ListComponents', method='ACCOUNT_COUNT')),
    ('L-0DF2752F', 'Image workflows',
     lambda c: dict(usage=len(c.call('imagebuilder', 'list_workflows', 'workflowVersionList')),
                    source='imagebuilder:ListWorkflows', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_imagebuilder(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'imagebuilder' for service, _ in context.quotas):
        return []
    return context.run('imagebuilder', CHECKS, skip)
