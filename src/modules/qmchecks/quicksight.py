"""Amazon QuickSight approval policy quotas.

The visual, sheet control and calculated field quotas live inside an analysis or
dashboard definition rather than in an inventory, the Quick Automate quotas have
no listing operation, and `Data Prep: Fields per dataset` counts fields inside a
dataset's data preparation tables, which `DataPrepConfiguration` exposes only as
source, transform and destination table maps. None of these is measured here.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

QUICKSIGHT = 'quicksight'
ASSET_TYPES = {'AGENT', 'SPACE', 'KNOWLEDGE_BASE'}


def approval_policies(ctx):
    found = {}
    for policy in ctx.call(QUICKSIGHT, 'list_approval_policies', 'Policies'):
        identity = policy.get('PolicyId')
        if not isinstance(identity, str) or not identity:
            raise NoData('QuickSight approval policy is missing its identity')
        found[identity] = policy
    return found


def _asset_types(policy):
    types = policy.get('AssetTypes')
    if not isinstance(types, list) or not types:
        raise NoData('QuickSight approval policy names no asset type')
    for asset in types:
        if asset not in ASSET_TYPES:
            raise NoData('QuickSight approval policy has an unknown asset type')
    return types


def policies_per_asset_type(ctx):
    counts = Counter()
    for policy in approval_policies(ctx).values():
        for asset in _asset_types(policy):
            counts[asset] += 1
    return maximum(((asset, count, None) for asset, count in counts.items()),
                   'QuickSightAssetType', 'quicksight:ListApprovalPolicies')


def _group_maximum(measure, resource_type='QuickSightApprovalPolicy'):
    def check(ctx):
        values = [(identity, measure(policy), None)
                  for identity, policy in approval_policies(ctx).items()]
        return maximum(values, resource_type, 'quicksight:ListApprovalPolicies')
    return check


def _applicable_groups(policy):
    applicable = policy.get('ApplicableTo')
    if not isinstance(applicable, dict) or not applicable.get('Type'):
        raise NoData('QuickSight approval policy has no applicable scope')
    groups = applicable.get('GroupArns') or []
    if not isinstance(groups, list):
        raise NoData('QuickSight approval policy has an invalid applicable group list')
    return len(groups)


def _approver_groups(policy):
    groups = policy.get('ApprovalGroups')
    if not isinstance(groups, list):
        raise NoData('QuickSight approval policy has no approver groups')
    return len(groups)


CHECKS = [
    ('L-D75C2D48', 'Maximum number of approval policies per account',
     lambda ctx: dict(usage=len(approval_policies(ctx)),
                      source='quicksight:ListApprovalPolicies',
                      method='ACCOUNT_COUNT')),
    ('L-8D8B7044', 'Maximum number of approval policies per asset type',
     policies_per_asset_type),
    ('L-04458D9F', 'Maximum applicable groups per approval policy',
     _group_maximum(_applicable_groups)),
    ('L-61EC97DA', 'Maximum approver groups per approval policy',
     _group_maximum(_approver_groups)),
]


def get_current_quotastatus_quicksight(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'quicksight' for service, _ in context.quotas):
        return []
    return context.run('quicksight', CHECKS, skip)
