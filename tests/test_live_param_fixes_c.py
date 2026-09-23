"""Request shapes the live IoT SiteWise and CloudTrail APIs accept."""
import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber

from modules.qmchecks import cloudtrail, sitewise
from modules.qmcore.aws import CheckContext, NoData, Unsupported

ACCOUNT = '123456789012'
MODEL = '11111111-1111-1111-1111-111111111111'
OTHER_MODEL = '22222222-2222-2222-2222-222222222222'
PARENT = '33333333-3333-3333-3333-333333333333'
CHILD = '44444444-4444-4444-4444-444444444444'
LEAF = '55555555-5555-5555-5555-555555555555'
OTHER_LEAF = '66666666-6666-6666-6666-666666666666'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def model(identifier, model_type):
    return {'id': identifier, 'arn': f'arn:aws:iotsitewise:eu-central-1:{ACCOUNT}:asset-model/'
            f'{identifier}', 'name': identifier, 'description': 'd', 'assetModelType': model_type,
            'creationDate': '2026-01-01T00:00:00Z', 'lastUpdateDate': '2026-01-01T00:00:00Z',
            'status': {'state': 'ACTIVE'}}


def asset(identifier, model_id):
    return {'id': identifier, 'arn': f'arn:aws:iotsitewise:eu-central-1:{ACCOUNT}:asset/'
            f'{identifier}', 'name': identifier, 'assetModelId': model_id,
            'creationDate': '2026-01-01T00:00:00Z', 'lastUpdateDate': '2026-01-01T00:00:00Z',
            'status': {'state': 'ACTIVE'}, 'hierarchies': []}


def test_interface_models_are_listed_apart_from_the_other_types():
    """ListAssetModels answers "The given filter is not supported" when
    INTERFACE is combined with another type."""
    ctx = context('iotsitewise', 'L-23AAE9E6')
    with Stubber(ctx.client('iotsitewise')) as stub:
        for model_type in ('ASSET_MODEL', 'COMPONENT_MODEL', 'INTERFACE'):
            stub.add_response('list_asset_models', {'assetModelSummaries': []},
                              {'assetModelTypes': [model_type]})
        assert check('L-23AAE9E6', sitewise.CHECKS)(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_child_assets_are_counted_for_every_asset_of_every_model():
    """ListAssets without a model only lists TOP_LEVEL assets; a parent can sit
    lower in the hierarchy, so the assets are listed per model."""
    ctx = context('iotsitewise', 'L-350DA9CF')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub.add_response('list_asset_models', {'assetModelSummaries': [
            model(MODEL, 'ASSET_MODEL'), model(OTHER_MODEL, 'ASSET_MODEL')]},
            {'assetModelTypes': ['ASSET_MODEL']})
        stub.add_response('list_assets', {'assetSummaries': [asset(PARENT, MODEL)]},
                          {'assetModelId': MODEL})
        stub.add_response('list_assets', {'assetSummaries': [asset(CHILD, OTHER_MODEL),
                                                             asset(LEAF, OTHER_MODEL)]},
                          {'assetModelId': OTHER_MODEL})
        children = {PARENT: [CHILD], CHILD: [LEAF, OTHER_LEAF], LEAF: []}
        for parent in (PARENT, CHILD, LEAF):
            stub.add_response('list_associated_assets', {'assetSummaries': [
                asset(child, OTHER_MODEL) for child in children[parent]]},
                {'assetId': parent, 'traversalDirection': 'CHILD'})
        result = check('L-350DA9CF', sitewise.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, CHILD)
        stub.assert_no_pending_responses()


def test_workspaces_not_launched_in_the_region_are_unsupported():
    ctx = context('iotsitewise', 'L-4C1CF6CB')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub.add_client_error('list_workspaces', 'InvalidRequestException',
                              'This feature is not supported yet', 400)
        with pytest.raises(Unsupported, match='workspaces'):
            check('L-4C1CF6CB', sitewise.CHECKS)(ctx)
    assert ctx.run('iotsitewise', sitewise.CHECKS[-2:])[0]['qualityStatus'] == 'UNSUPPORTED'


def test_other_invalid_workspace_requests_stay_errors():
    ctx = context('iotsitewise', 'L-55758B95')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub.add_client_error('list_workspaces', 'InvalidRequestException',
                              'Something else is wrong', 400)
        with pytest.raises(ClientError):
            check('L-55758B95', sitewise.CHECKS)(ctx)


def trail(name, account=ACCOUNT, region='eu-central-1', organization=False):
    return {'Name': name, 'TrailARN': f'arn:aws:cloudtrail:{region}:{account}:trail/{name}',
            'HomeRegion': region, 'IsOrganizationTrail': organization,
            'IsMultiRegionTrail': True}


@pytest.mark.parametrize('code', ['L-9387CED7', 'L-71DEA5C6', 'L-203ED99D'])
def test_selectors_are_read_only_for_trails_this_account_owns_here(code):
    """An organization trail owned by the management account and a multi-Region
    trail homed elsewhere are shadows: GetEventSelectors by name fails for the
    first, and both are measured where they live."""
    ctx = context('cloudtrail', code)
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [
            trail('aws-controltower-BaselineCloudTrail', account='005439271728',
                  organization=True),
            trail('elsewhere', region='us-east-1'),
            trail('own')]}, {})
        stub.add_response('get_event_selectors', {
            'TrailARN': f'arn:aws:cloudtrail:eu-central-1:{ACCOUNT}:trail/own',
            'EventSelectors': [{'ReadWriteType': 'All', 'IncludeManagementEvents': True,
                                'DataResources': []}]}, {'TrailName': 'own'})
        result = check(code, cloudtrail.CHECKS)(ctx)
        assert result['resource_id'] == 'own'
        stub.assert_no_pending_responses()


def test_only_shadow_trails_leave_no_trail_to_measure():
    ctx = context('cloudtrail', 'L-9387CED7')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [
            trail('org', account='005439271728', organization=True)]}, {})
        result = check('L-9387CED7', cloudtrail.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (0, None)
        stub.assert_no_pending_responses()


def test_a_trail_without_a_valid_arn_is_reported():
    ctx = context('cloudtrail', 'L-9387CED7')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [
            {'Name': 'one', 'HomeRegion': 'eu-central-1'}]}, {})
        with pytest.raises(NoData, match='ARN'):
            check('L-9387CED7', cloudtrail.CHECKS)(ctx)
