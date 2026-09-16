"""AWS Service Quotas pending quota increase request quotas."""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SERVICE_QUOTAS = 'service-quotas'
REQUEST_STATES = {'PENDING', 'CASE_OPENED', 'APPROVED', 'DENIED', 'CASE_CLOSED',
                  'NOT_APPROVED', 'INVALID_REQUEST'}
# A request occupies the quota until AWS has decided it.
ACTIVE_STATES = {'PENDING', 'CASE_OPENED'}


def active_requests(ctx):
    found = {}
    for request in ctx.call(SERVICE_QUOTAS, 'list_requested_service_quota_change_history',
                            'RequestedQuotas'):
        identity = request.get('Id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Quota increase request is missing its identity')
        if request.get('Status') not in REQUEST_STATES:
            raise NoData('Quota increase request has an unknown status')
        if request['Status'] in ACTIVE_STATES:
            found[identity] = request
    return found


def requests_per_quota(ctx):
    counts = Counter()
    for request in active_requests(ctx).values():
        service, quota = request.get('ServiceCode'), request.get('QuotaCode')
        if not isinstance(service, str) or not isinstance(quota, str):
            raise NoData('Quota increase request names no quota')
        counts[f'{service}/{quota}'] += 1
    return maximum(((quota, count, None) for quota, count in counts.items()),
                   'ServiceQuota',
                   'service-quotas:ListRequestedServiceQuotaChangeHistory')


CHECKS = [
    ('L-89094105', 'Active requests per account per opt-in Region',
     lambda ctx: dict(usage=len(active_requests(ctx)),
                      source='service-quotas:ListRequestedServiceQuotaChangeHistory',
                      method='ACCOUNT_COUNT')),
    ('L-36BDD542', 'Active requests per quota', requests_per_quota),
]


def get_current_quotastatus_servicequotas(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'servicequotas' for service, _ in context.quotas):
        return []
    return context.run('servicequotas', CHECKS, skip)
