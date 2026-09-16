"""CloudHSM regional cluster counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-4B16B391', 'Clusters per AWS Region and AWS account',
     lambda c: dict(usage=len(c.call('cloudhsmv2', 'describe_clusters', 'Clusters')),
                    source='cloudhsmv2:DescribeClusters', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_cloudhsm(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'cloudhsm' for service, _ in context.quotas):
        return []
    return context.run('cloudhsm', CHECKS, skip)
