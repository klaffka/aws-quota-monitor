"""Amazon QuickSight approval policy and definition quotas.

The visual, sheet control and calculated field quotas live inside an analysis or
dashboard definition rather than in an inventory. That is where they are read
from: the definition is not listed, but it is reachable, because
DescribeAnalysisDefinition and DescribeDashboardDefinition return it whole for
every asset ListAnalyses and ListDashboards name. Both kinds are walked;
reading only analyses would report a confident undercount for every dashboard.

Three quotas stay open. The Quick Automate limits name automations and
automation groups: the SDK ships ListFlows, but a flow is not an automation --
DescribeAutomationJob takes an AutomationGroupId and an AutomationId, and there
is no listing for either, so mapping one onto the other would be a guess.
`Data Prep: Fields per dataset` counts fields inside a dataset's data
preparation tables, which DataPrepConfiguration exposes only as source,
transform and destination table maps. `Email aliases per group for email
reports` has no operation at all.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

QUICKSIGHT = 'quicksight'
ASSET_TYPES = {'AGENT', 'SPACE', 'KNOWLEDGE_BASE'}
# QuickSight reports an asset's lifecycle as <VERB>_<STATE>. Only a finished
# create or update has a definition to read; the rest have nothing to describe.
RESOURCE_STATES = {'CREATION_IN_PROGRESS', 'CREATION_SUCCESSFUL', 'CREATION_FAILED',
                   'UPDATE_IN_PROGRESS', 'UPDATE_SUCCESSFUL', 'UPDATE_FAILED',
                   'DELETED'}
READABLE_STATES = {'CREATION_SUCCESSFUL', 'UPDATE_SUCCESSFUL'}
DEFINITION_SOURCE = ('quicksight:DescribeAnalysisDefinition'
                     '+DescribeDashboardDefinition')


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


def _readable(status, subject):
    """Say whether an asset has a definition, refusing an unknown state."""
    if status not in RESOURCE_STATES:
        raise NoData(f'QuickSight {subject} has an unknown status')
    return status in READABLE_STATES


def _asset_identity(summary, field, subject):
    identity = summary.get(field)
    if not isinstance(identity, str) or not identity:
        raise NoData(f'QuickSight {subject} is missing its identity')
    return identity


def definitions(ctx):
    """Return (asset id, definition) for every analysis and dashboard holding one."""
    found = []
    for summary in ctx.call(QUICKSIGHT, 'list_analyses', 'AnalysisSummaryList',
                            AwsAccountId=ctx.account):
        identity = _asset_identity(summary, 'AnalysisId', 'analysis')
        if not _readable(summary.get('Status'), 'analysis'):
            continue
        response = ctx.call(QUICKSIGHT, 'describe_analysis_definition',
                            AwsAccountId=ctx.account, AnalysisId=identity)
        found.append((identity, response.get('Definition') or {}))
    for summary in ctx.call(QUICKSIGHT, 'list_dashboards', 'DashboardSummaryList',
                            AwsAccountId=ctx.account):
        identity = _asset_identity(summary, 'DashboardId', 'dashboard')
        # A dashboard summary carries no status, so the describe response has it.
        response = ctx.call(QUICKSIGHT, 'describe_dashboard_definition',
                            AwsAccountId=ctx.account, DashboardId=identity)
        if not _readable(response.get('ResourceStatus'), 'dashboard'):
            continue
        found.append((identity, response.get('Definition') or {}))
    return found


def _union(entry, subject):
    """Return the bodies a union holds; the API populates exactly one of them.

    Taking every populated member keeps the answer identical against the API
    while leaving the check exercised by the shape harness, which fills them all.
    """
    bodies = [body for body in entry.values() if isinstance(body, dict)]
    if not bodies:
        raise NoData(f'QuickSight {subject} names no type')
    return bodies


def _sheets(definition):
    """Yield every sheet, including the tooltip sheets that also hold visuals."""
    for sheet in (list(definition.get('Sheets') or ())
                  + list(definition.get('TooltipSheets') or ())):
        yield _asset_identity(sheet, 'SheetId', 'sheet'), sheet


def _visuals(definition, asset):
    for sheet_id, sheet in _sheets(definition):
        for entry in sheet.get('Visuals') or ():
            for body in _union(entry, 'visual'):
                identity = _asset_identity(body, 'VisualId', 'visual')
                yield f'{asset}/{sheet_id}/{identity}', body


def _actions(definition, asset):
    for label, body in _visuals(definition, asset):
        for entry in body.get('Actions') or ():
            identity = _asset_identity(entry, 'CustomActionId', 'custom action')
            yield f'{label}/{identity}', entry


def _controls(definition, asset):
    for sheet_id, sheet in _sheets(definition):
        for kind in ('ParameterControls', 'FilterControls'):
            for entry in sheet.get(kind) or ():
                for body in _union(entry, 'sheet control'):
                    identity = (body.get('ParameterControlId')
                                or body.get('FilterControlId'))
                    if not isinstance(identity, str) or not identity:
                        raise NoData('QuickSight sheet control is missing its identity')
                    yield f'{asset}/{sheet_id}/{identity}', body


def _control_values(body):
    """The values a control lists itself; one bound to a column lists none."""
    return (body.get('SelectableValues') or {}).get('Values') or ()


def _over_definitions(walk, resource_type):
    """Take the maximum of one measure over every asset's definition."""
    def check(ctx):
        values = [value for asset, definition in definitions(ctx)
                  for value in walk(definition, asset)]
        return maximum(values, resource_type, DEFINITION_SOURCE)
    return check


def _visual_actions(definition, asset):
    for label, body in _visuals(definition, asset):
        yield label, len(body.get('Actions') or ()), None


def _action_name_lengths(definition, asset):
    for label, entry in _actions(definition, asset):
        name = entry.get('Name')
        if not isinstance(name, str) or not name:
            raise NoData('QuickSight custom action is missing its name')
        yield label, len(name), None


def _hyperlink_lengths(definition, asset):
    for label, entry in _actions(definition, asset):
        for operation in entry.get('ActionOperations') or ():
            template = (operation.get('URLOperation') or {}).get('URLTemplate')
            if template is None:
                continue
            if not isinstance(template, str) or not template:
                raise NoData('QuickSight URL action has no hyperlink')
            yield label, len(template), None


def _expression_lengths(definition, asset):
    for field in definition.get('CalculatedFields') or ():
        name = _asset_identity(field, 'Name', 'calculated field')
        expression = field.get('Expression')
        if not isinstance(expression, str) or not expression:
            raise NoData('QuickSight calculated field has no expression')
        yield f'{asset}/{name}', len(expression), None


def _control_item_counts(definition, asset):
    for label, body in _controls(definition, asset):
        yield label, len(_control_values(body)), None


def _control_value_lengths(definition, asset):
    for label, body in _controls(definition, asset):
        for value in _control_values(body):
            if not isinstance(value, str) or not value:
                raise NoData('QuickSight sheet control has an empty value')
            yield label, len(value), None


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
    ('L-E43AEF3C', 'Custom actions per visual',
     _over_definitions(_visual_actions, 'QuickSightVisual')),
    ('L-B8F293B6', 'Custom action name length',
     _over_definitions(_action_name_lengths, 'QuickSightCustomAction')),
    ('L-C1F9B371', 'URL action hyperlink length',
     _over_definitions(_hyperlink_lengths, 'QuickSightCustomAction')),
    ('L-AECE65ED', 'Calculated field expression length',
     _over_definitions(_expression_lengths, 'QuickSightCalculatedField')),
    ('L-E9E486C4', 'Display items per sheet control',
     _over_definitions(_control_item_counts, 'QuickSightSheetControl')),
    ('L-843701D0', 'Maximum number of characters per specified Control values',
     _over_definitions(_control_value_lengths, 'QuickSightSheetControl')),
]


def get_current_quotastatus_quicksight(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'quicksight' for service, _ in context.quotas):
        return []
    return context.run('quicksight', CHECKS, skip)
