"""IoT SiteWise portal, project and dashboard scopes."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import sitewise
from modules.qmcore.aws import CheckContext, NoData


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'iotsitewise', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in sitewise.CHECKS if quota == code)


def portal(identity):
    return {'id': identity, 'name': identity, 'startUrl': 'https://example.com',
            'status': {'state': 'ACTIVE'}}


# SiteWise ids are 36-character UUIDs; the model enforces the length.
def uid(label):
    return f'{label}-' + 'x' * (36 - len(label) - 1)


PORTAL_ONE, PORTAL_TWO = uid('portal1'), uid('portal2')
PROJECT_A, PROJECT_B, PROJECT_C = uid('proja'), uid('projb'), uid('projc')
PORTALS = {'portalSummaries': [portal(PORTAL_ONE), portal(PORTAL_TWO)]}
PROJECTS = {PORTAL_ONE: [PROJECT_A], PORTAL_TWO: [PROJECT_B, PROJECT_C]}


def stub_projects(stub):
    stub.add_response('list_portals', PORTALS, {})
    for portal_id, projects in PROJECTS.items():
        stub.add_response('list_projects',
                          {'projectSummaries': [{'id': p, 'name': p} for p in projects]},
                          {'portalId': portal_id})


def test_projects_use_the_largest_portal():
    ctx = context('L-116F669B')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub_projects(stub)
        result = check('L-116F669B')(ctx)
        assert (result['usage'], result['resource_id']) == (2, PORTAL_TWO)
        stub.assert_no_pending_responses()


def test_dashboards_use_the_largest_project_across_every_portal():
    """Projects live under a portal, so the walk has to cross both."""
    ctx = context('L-81C6A4F0')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub_projects(stub)
        for project, count in [(PROJECT_A, 3), (PROJECT_B, 1), (PROJECT_C, 2)]:
            stub.add_response('list_dashboards', {'dashboardSummaries': [
                {'id': uid(f'dash{index}'), 'name': f'd{index}'} for index in range(count)]},
                {'projectId': project})
        result = check('L-81C6A4F0')(ctx)
        assert (result['usage'], result['resource_id']) == (3, PROJECT_A)
        stub.assert_no_pending_responses()


def test_root_assets_use_the_largest_project():
    ctx = context('L-AF558AF7')
    with Stubber(ctx.client('iotsitewise')) as stub:
        stub_projects(stub)
        for project, assets in [(PROJECT_A, [uid('a1')]),
                                (PROJECT_B, [uid('b1'), uid('b2'), uid('b3')]),
                                (PROJECT_C, [])]:
            stub.add_response('list_project_assets', {'assetIds': assets},
                              {'projectId': project})
        result = check('L-AF558AF7')(ctx)
        assert (result['usage'], result['resource_id']) == (3, PROJECT_B)
        stub.assert_no_pending_responses()


def test_a_portal_without_an_identity_is_reported_as_no_data():
    from unittest.mock import Mock

    ctx = Mock()
    ctx.call.return_value = [{'name': 'nameless'}]
    with pytest.raises(NoData, match='portal'):
        check('L-116F669B')(ctx)
