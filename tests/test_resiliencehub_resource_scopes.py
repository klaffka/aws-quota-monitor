"""Resilience Hub scopes that a resource listing and a service detail report."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import resiliencehub
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'resiliencehub', 'QuotaCode': code,
                          'Value': 100}], account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in resiliencehub.CHECKS if quota == code)


def app_arn(name):
    return f'arn:aws:resiliencehub:{REGION}:{ACCOUNT}:app/{name}'


def service_arn(name):
    return f'arn:aws:resiliencehub:{REGION}:{ACCOUNT}:service/{name}'


def resource(name, components):
    return {'logicalResourceId': {'identifier': name},
            'physicalResourceId': {'identifier': name, 'type': 'Arn'},
            'resourceType': 'AWS::EC2::Instance', 'resourceName': name,
            'appComponents': [{'name': f'c{index}', 'type': 'AWS::ResilienceHub::ComputeAppComponent'}
                              for index in range(components)]}


def stub_resources(stub, apps):
    """Stub the app walk: the app listing, then versions and resources per app."""
    stub.add_response('list_apps', {'appSummaries': [
        {'appArn': app_arn(name), 'name': name, 'creationTime': 1,
         'complianceStatus': 'NotAssessed'} for name in apps]}, {})
    for name, resources in apps.items():
        stub.add_response('list_app_versions',
                          {'appVersions': [{'appVersion': 'release'}]},
                          {'appArn': app_arn(name)})
        stub.add_response('list_app_version_resources',
                          {'physicalResources': list(resources),
                           'resolutionId': 'r1'},
                          {'appArn': app_arn(name), 'appVersion': 'release'})


def test_the_resource_carrying_the_most_app_components_is_measured():
    ctx = context('L-3DCDC079')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub_resources(stub, {'one': [resource('quiet', 1), resource('busy', 4)]})
        result = check('L-3DCDC079')(ctx)
        assert (result['usage'], result['resource_id']) == (4, f'{app_arn("one")}/busy')
        stub.assert_no_pending_responses()


def test_resources_are_compared_across_applications():
    ctx = context('L-3DCDC079')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub_resources(stub, {'one': [resource('a', 2)], 'two': [resource('b', 5)]})
        result = check('L-3DCDC079')(ctx)
        assert (result['usage'], result['resource_id']) == (5, f'{app_arn("two")}/b')
        stub.assert_no_pending_responses()


def test_a_resource_in_no_app_component_counts_as_zero():
    ctx = context('L-3DCDC079')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub_resources(stub, {'one': [resource('bare', 0)]})
        result = check('L-3DCDC079')(ctx)
        assert (result['usage'], result['resource_id']) == (0, f'{app_arn("one")}/bare')
        stub.assert_no_pending_responses()


def test_an_account_without_applications_counts_as_zero():
    ctx = context('L-3DCDC079')
    with Stubber(ctx.client('resiliencehub')) as stub:
        stub.add_response('list_apps', {'appSummaries': []}, {})
        assert check('L-3DCDC079')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_resource_without_a_name_is_reported():
    """The logical id is a required member, so only a broken response omits it."""
    ctx = FakeContext({
        'list_apps': [{'appArn': app_arn('one')}],
        'list_app_versions': [{'appVersion': 'release'}],
        'list_app_version_resources': [{'logicalResourceId': {},
                                        'resourceType': 'AWS::EC2::Instance'}]})
    with pytest.raises(NoData, match='identity'):
        check('L-3DCDC079')(ctx)


def stub_services(stub, services):
    """Stub the second-generation service listing, then each service detail."""
    stub.add_response('list_services', {'serviceSummaries': [
        {'serviceArn': service_arn(name), 'name': name}
        for name in services]}, {})
    for name, roles in services.items():
        service = {'serviceArn': service_arn(name), 'name': name}
        if roles is not None:
            service['permissionModel'] = {'invokerRoleName': 'invoker',
                                          'crossAccountRoles': list(roles)}
        stub.add_response('get_service', {'service': service},
                          {'serviceArn': service_arn(name)})


def role_arn(index):
    return {'crossAccountRoleArn': f'arn:aws:iam::99999999999{index}:role/resiliencehub'}


class FakeContext:
    """A context answering by method, for responses the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_the_service_holding_the_most_cross_account_roles_is_measured():
    ctx = context('L-BC37F660')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub_services(stub, {'quiet': [role_arn(1)],
                             'busy': [role_arn(1), role_arn(2), role_arn(3)]})
        result = check('L-BC37F660')(ctx)
        assert (result['usage'], result['resource_id']) == (3, service_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_service_running_in_one_account_holds_no_cross_account_role():
    """A service with no permission model at all reaches across no account."""
    ctx = context('L-BC37F660')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub_services(stub, {'local': None})
        result = check('L-BC37F660')(ctx)
        assert (result['usage'], result['resource_id']) == (0, service_arn('local'))
        stub.assert_no_pending_responses()


def test_an_account_without_services_counts_as_zero():
    ctx = context('L-BC37F660')
    with Stubber(ctx.client('resiliencehubv2')) as stub:
        stub.add_response('list_services', {'serviceSummaries': []}, {})
        assert check('L-BC37F660')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_service_detail_that_names_no_service_is_reported():
    """GetService always returns a service, so only a broken response omits it."""
    ctx = FakeContext({'list_services': [{'serviceArn': service_arn('odd'),
                                          'name': 'odd'}],
                       'get_service': {}})
    with pytest.raises(NoData, match='detail'):
        check('L-BC37F660')(ctx)
