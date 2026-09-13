"""AWS Well-Architected regional resource counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-ACECEBBD', 'Workloads per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_workloads', 'WorkloadSummaries')), source='wellarchitected:ListWorkloads', method='ACCOUNT_COUNT')),
    ('L-BAE0003F', 'Lenses per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_lenses', 'LensSummaries')), source='wellarchitected:ListLenses', method='ACCOUNT_COUNT')),
    ('L-D69BFA30', 'Review templates per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_review_templates', 'ReviewTemplates')), source='wellarchitected:ListReviewTemplates', method='ACCOUNT_COUNT')),
]

def get_current_quotastatus_wellarchitected(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'wellarchitected' for service, _ in context.quotas): return []
    return context.run('wellarchitected', CHECKS, skip)
