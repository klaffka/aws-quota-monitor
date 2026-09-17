"""QuickSight quotas that live inside an analysis or dashboard definition."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import quicksight
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'quicksight', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in quicksight.CHECKS if quota == code)


def visual(identity, actions=(), kind='TableVisual'):
    return {kind: {'VisualId': identity, 'Actions': list(actions)}}


def action(identity, name='action', url=None):
    """A custom action; the SDK requires at least one operation, so it navigates."""
    operation = ({'URLOperation': {'URLTemplate': url, 'URLTarget': 'NEW_TAB'}}
                 if url is not None else {'NavigationOperation': {}})
    return {'CustomActionId': identity, 'Name': name, 'Trigger': 'DATA_POINT_CLICK',
            'ActionOperations': [operation]}


def sheet(identity, visuals=(), parameter_controls=(), filter_controls=()):
    return {'SheetId': identity, 'Visuals': list(visuals),
            'ParameterControls': list(parameter_controls),
            'FilterControls': list(filter_controls)}


def list_control(identity, values=None, linked=False):
    """A parameter list control, either with static values or bound to a column."""
    selectable = {}
    if values is not None:
        selectable['Values'] = list(values)
    if linked:
        selectable['LinkToDataSetColumn'] = {'DataSetIdentifier': 'ds',
                                             'ColumnName': 'country'}
    return {'List': {'ParameterControlId': identity, 'Title': identity,
                     'SourceParameterName': 'p', 'SelectableValues': selectable}}


def stub_assets(stub, analyses=(), dashboards=()):
    """Stub the walk in the order the checks make it: analyses, then dashboards.

    ``analyses`` and ``dashboards`` hold ``(identity, status, definition)``; a
    definition of ``None`` means the asset is never described.
    """
    stub.add_response('list_analyses', {'AnalysisSummaryList': [
        {'AnalysisId': identity, 'Name': identity, 'Status': status}
        for identity, status, _ in analyses]}, {'AwsAccountId': ACCOUNT})
    for identity, _status, definition in analyses:
        if definition is None:
            continue
        stub.add_response('describe_analysis_definition',
                          {'AnalysisId': identity, 'Definition': definition},
                          {'AwsAccountId': ACCOUNT, 'AnalysisId': identity})
    stub.add_response('list_dashboards', {'DashboardSummaryList': [
        {'DashboardId': identity, 'Name': identity}
        for identity, _, _ in dashboards]}, {'AwsAccountId': ACCOUNT})
    for identity, status, definition in dashboards:
        response = {'DashboardId': identity, 'ResourceStatus': status}
        if definition is not None:
            response['Definition'] = definition
        stub.add_response('describe_dashboard_definition', response,
                          {'AwsAccountId': ACCOUNT, 'DashboardId': identity})


def tooltip_sheet(identity, visuals=()):
    """A tooltip sheet holds visuals but, unlike a sheet, no controls."""
    return {'SheetId': identity, 'Visuals': list(visuals)}


def definition(sheets=(), calculated_fields=(), tooltip_sheets=()):
    return {'DataSetIdentifierDeclarations': [], 'Sheets': list(sheets),
            'TooltipSheets': list(tooltip_sheets),
            'CalculatedFields': list(calculated_fields)}


def test_the_busiest_visual_is_found_across_analyses_and_dashboards():
    """A dashboard's visuals count too; reading only analyses would undercount."""
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(
            stub,
            analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
                sheets=[sheet('s1', visuals=[visual('v1', [action('c1')])])]))],
            dashboards=[('d1', 'UPDATE_SUCCESSFUL', definition(
                sheets=[sheet('s9', visuals=[
                    visual('v9', [action('c1'), action('c2'), action('c3')])])]))])
        result = check('L-E43AEF3C')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'd1/s9/v9')
        stub.assert_no_pending_responses()


def test_a_visual_in_a_tooltip_sheet_is_counted_as_well():
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            tooltip_sheets=[tooltip_sheet('t1', visuals=[
                visual('v1', [action('c1'), action('c2')])])]))])
        result = check('L-E43AEF3C')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'a1/t1/v1')
        stub.assert_no_pending_responses()


def test_an_empty_account_counts_as_zero():
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub)
        assert check('L-E43AEF3C')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('status', ['DELETED', 'CREATION_IN_PROGRESS',
                                    'CREATION_FAILED'])
def test_an_analysis_that_holds_no_readable_definition_is_not_described(status):
    """Describing a deleted or half-built analysis would fail the whole check."""
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', status, None)])
        assert check('L-E43AEF3C')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_status_the_sdk_does_not_name_is_reported():
    """Guessing at an unknown lifecycle state would silently drop an analysis."""
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'ARCHIVED', None)])
        with pytest.raises(NoData, match='status'):
            check('L-E43AEF3C')(ctx)


def test_a_dashboard_whose_definition_is_not_ready_is_skipped():
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, dashboards=[('d1', 'UPDATE_FAILED', None)])
        assert check('L-E43AEF3C')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_visual_without_an_identity_is_reported():
    """The SDK cannot produce this, so the guard is exercised on the walk itself."""
    walk = quicksight._visuals(definition(
        sheets=[{'SheetId': 's1', 'Visuals': [{'TableVisual': {'Actions': []}}]}]), 'a1')
    with pytest.raises(NoData, match='identity'):
        list(walk)


def test_a_visual_type_carrying_no_actions_counts_as_zero():
    """LayerMapVisual has no Actions member at all, so it holds none."""
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', visuals=[{'LayerMapVisual': {'VisualId': 'v1'}}])]))])
        result = check('L-E43AEF3C')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'a1/s1/v1')
        stub.assert_no_pending_responses()


def test_the_longest_custom_action_name_is_measured():
    ctx = context('L-B8F293B6')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', visuals=[visual('v1', [
                action('c1', name='short'),
                action('c2', name='a considerably longer action name')])])]))])
        result = check('L-B8F293B6')(ctx)
        assert (result['usage'], result['resource_id']) == (33, 'a1/s1/v1/c2')
        stub.assert_no_pending_responses()


def test_the_longest_url_action_hyperlink_is_measured():
    ctx = context('L-C1F9B371')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', visuals=[visual('v1', [
                action('c1', url='https://example.test/a'),
                action('c2', url='https://example.test/a/longer/target')])])]))])
        result = check('L-C1F9B371')(ctx)
        assert (result['usage'], result['resource_id']) == (36, 'a1/s1/v1/c2')
        stub.assert_no_pending_responses()


def test_an_action_that_opens_no_url_is_left_out_of_the_hyperlink_maximum():
    """A filter or navigation action has no hyperlink to measure."""
    ctx = context('L-C1F9B371')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', visuals=[visual('v1', [action('c1')])])]))])
        assert check('L-C1F9B371')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_the_longest_calculated_field_expression_is_measured():
    ctx = context('L-AECE65ED')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            calculated_fields=[
                {'DataSetIdentifier': 'ds', 'Name': 'plain', 'Expression': 'sum({x})'},
                {'DataSetIdentifier': 'ds', 'Name': 'rich',
                 'Expression': 'ifelse({x} > 0, sum({x}), 0)'}]))])
        result = check('L-AECE65ED')(ctx)
        assert (result['usage'], result['resource_id']) == (28, 'a1/rich')
        stub.assert_no_pending_responses()


def test_a_calculated_field_without_an_expression_is_reported():
    """The SDK cannot produce this, so the guard is exercised on the walk itself."""
    walk = quicksight._expression_lengths(definition(
        calculated_fields=[{'DataSetIdentifier': 'ds', 'Name': 'plain'}]), 'a1')
    with pytest.raises(NoData, match='expression'):
        list(walk)


def test_the_fullest_sheet_control_is_measured():
    ctx = context('L-E9E486C4')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1',
                          parameter_controls=[list_control('p1', values=['a', 'b'])],
                          filter_controls=[{'List': {
                              'FilterControlId': 'f1', 'Title': 'f1',
                              'SourceFilterId': 'flt',
                              'SelectableValues': {'Values': ['a', 'b', 'c']}}}])]))])
        result = check('L-E9E486C4')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'a1/s1/f1')
        stub.assert_no_pending_responses()


def test_a_control_bound_to_a_dataset_column_counts_as_zero():
    """The column's values are not part of the definition, so none are listed."""
    ctx = context('L-E9E486C4')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', parameter_controls=[list_control('p1', linked=True)])]))])
        result = check('L-E9E486C4')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'a1/s1/p1')
        stub.assert_no_pending_responses()


def test_a_control_that_offers_no_value_list_counts_as_zero():
    """A slider or text field has no items to display."""
    ctx = context('L-E9E486C4')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', parameter_controls=[{'TextField': {
                'ParameterControlId': 'p1', 'Title': 'p1',
                'SourceParameterName': 'p'}}])]))])
        result = check('L-E9E486C4')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'a1/s1/p1')
        stub.assert_no_pending_responses()


def test_the_longest_control_value_is_measured():
    ctx = context('L-843701D0')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', parameter_controls=[
                list_control('p1', values=['ab', 'a much longer value'])])]))])
        result = check('L-843701D0')(ctx)
        assert (result['usage'], result['resource_id']) == (19, 'a1/s1/p1')
        stub.assert_no_pending_responses()


def test_one_walk_answers_every_definition_quota():
    """The six checks share a run, so the inventory is read once per run."""
    ctx = context('L-E43AEF3C')
    with Stubber(ctx.client('quicksight')) as stub:
        stub_assets(stub, analyses=[('a1', 'CREATION_SUCCESSFUL', definition(
            sheets=[sheet('s1', visuals=[visual('v1', [action('c1', url='https://x')])],
                          parameter_controls=[list_control('p1', values=['a'])])],
            calculated_fields=[{'DataSetIdentifier': 'ds', 'Name': 'f',
                                'Expression': 'sum({x})'}]))])
        assert check('L-E43AEF3C')(ctx)['usage'] == 1
        assert check('L-E9E486C4')(ctx)['usage'] == 1
        assert check('L-AECE65ED')(ctx)['usage'] == 8
        stub.assert_no_pending_responses()
