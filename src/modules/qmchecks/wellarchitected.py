"""AWS Well-Architected regional resource counts."""
from modules.qmcore.aws import NoData, maximum, CheckContext, session_from_env

def _shares(ctx, parents, parent_key, field, method, key, resource, **parent_kwargs):
    """Count the shares of each parent, which are only listable per parent."""
    values = []
    for parent in ctx.call('wellarchitected', parents, parent_key, **parent_kwargs):
        identity = parent.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'Well-Architected {resource} is missing its identity')
        shares = ctx.call('wellarchitected', method, key, **{field: identity})
        values.append((identity, len(shares), None))
    return maximum(values, resource, f'wellarchitected:{method}')


CHECKS = [
    ('L-ACECEBBD', 'Workloads per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_workloads', 'WorkloadSummaries')), source='wellarchitected:ListWorkloads', method='ACCOUNT_COUNT')),
    ('L-BAE0003F', 'Lenses per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_lenses', 'LensSummaries')), source='wellarchitected:ListLenses', method='ACCOUNT_COUNT')),
    ('L-D69BFA30', 'Review templates per account per Region', lambda c: dict(usage=len(c.call('wellarchitected', 'list_review_templates', 'ReviewTemplates')), source='wellarchitected:ListReviewTemplates', method='ACCOUNT_COUNT')),
    # A shared or AWS-owned lens cannot be shared on, so only the lenses this
    # account owns hold the quota.
    ('L-E62A1DE4', 'Shares per lens',
     lambda ctx: _shares(ctx, 'list_lenses', 'LensSummaries', 'LensAlias',
                         'list_lens_shares', 'LensShareSummaries',
                         'WellArchitectedLens', LensType='CUSTOM_SELF')),
    ('L-7E98904D', 'Shares per workload',
     lambda ctx: _shares(ctx, 'list_workloads', 'WorkloadSummaries', 'WorkloadId',
                         'list_workload_shares', 'WorkloadShareSummaries',
                         'WellArchitectedWorkload')),
    ('L-A5DDC022', 'Shares per review template',
     lambda ctx: _shares(ctx, 'list_review_templates', 'ReviewTemplates',
                         'TemplateArn', 'list_template_shares',
                         'TemplateShareSummaries', 'WellArchitectedReviewTemplate')),
]

def get_current_quotastatus_wellarchitected(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'wellarchitected' for service, _ in context.quotas): return []
    return context.run('wellarchitected', CHECKS, skip)
