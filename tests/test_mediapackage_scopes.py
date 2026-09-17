"""MediaPackage packaging group scopes and harvest job concurrency."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import mediapackage
from modules.qmcore.aws import CheckContext, NoData

MOMENT = '2026-09-16T00:00:00Z'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'mediapackage', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in mediapackage.CHECKS if quota == code)


def group(identity):
    return {'Id': identity, 'CreatedAt': MOMENT,
            'Arn': f'arn:aws:mediapackage-vod:eu-central-1:1:packaging-groups/{identity}'}


def test_packaging_groups_are_counted_for_the_account():
    ctx = context('L-66FFDBE4')
    with Stubber(ctx.client('mediapackage-vod')) as stub:
        stub.add_response('list_packaging_groups',
                          {'PackagingGroups': [group('busy'), group('quiet')]}, {})
        result = check('L-66FFDBE4')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, method, key', [
    ('L-1E1258F1', 'list_packaging_configurations', 'PackagingConfigurations'),
    ('L-563EE697', 'list_assets', 'Assets'),
])
def test_children_are_counted_against_the_group_they_name(code, method, key):
    """Both listings answer for the account and name their packaging group."""
    ctx = context(code)
    with Stubber(ctx.client('mediapackage-vod')) as stub:
        stub.add_response(method, {key: [
            {'Id': 'one', 'PackagingGroupId': 'busy', 'CreatedAt': MOMENT},
            {'Id': 'two', 'PackagingGroupId': 'busy', 'CreatedAt': MOMENT},
            {'Id': 'three', 'PackagingGroupId': 'quiet', 'CreatedAt': MOMENT}]}, {})
        result = check(code)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'busy')
        stub.assert_no_pending_responses()


def test_an_entry_without_its_group_is_reported():
    ctx = context('L-563EE697')
    with Stubber(ctx.client('mediapackage-vod')) as stub:
        stub.add_response('list_assets', {'Assets': [{'Id': 'orphan', 'CreatedAt': MOMENT}]}, {})
        with pytest.raises(NoData, match='packaging group'):
            check('L-563EE697')(ctx)


def test_only_running_harvest_jobs_count_towards_concurrency():
    """MediaPackage filters by status server side, so one call is enough."""
    ctx = context('L-B1B90B42')
    with Stubber(ctx.client('mediapackage')) as stub:
        stub.add_response('list_harvest_jobs', {'HarvestJobs': [
            {'Id': 'h1', 'Status': 'IN_PROGRESS'}, {'Id': 'h2', 'Status': 'IN_PROGRESS'}]},
            {'IncludeStatus': 'IN_PROGRESS'})
        result = check('L-B1B90B42')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()
