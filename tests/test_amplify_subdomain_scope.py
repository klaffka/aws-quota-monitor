"""Amplify subdomains, read from the domain listing the app walk already makes."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import amplify
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'
CODE = 'L-85685B2E'


def context(code=CODE):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'amplify', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code=CODE):
    return next(fn for quota, _name, fn in amplify.CHECKS if quota == code)


def app(app_id):
    return {'appId': app_id, 'appArn': f'arn:app/{app_id}', 'name': app_id,
            'description': '', 'repository': '', 'platform': 'WEB',
            'createTime': 1, 'updateTime': 1, 'environmentVariables': {},
            'defaultDomain': f'{app_id}.amplifyapp.test',
            'enableBranchAutoBuild': False, 'enableBasicAuth': False}


def domain(name, subdomains):
    return {'domainAssociationArn': f'arn:domain/{name}', 'domainName': name,
            'enableAutoSubDomain': False, 'domainStatus': 'AVAILABLE',
            'statusReason': '',
            'subDomains': [
                {'subDomainSetting': {'prefix': f'p{index}', 'branchName': 'main'},
                 'verified': True, 'dnsRecord': 'record'}
                for index in range(subdomains)]}


def stub_domains(stub, apps):
    """``apps`` maps an app id to a mapping of domain name to subdomain count."""
    stub.add_response('list_apps', {'apps': [app(app_id) for app_id in apps]}, {})
    for app_id, domains in apps.items():
        stub.add_response('list_domain_associations', {'domainAssociations': [
            domain(name, count) for name, count in domains.items()]},
            {'appId': app_id})


def test_the_domain_with_the_most_subdomains_is_measured():
    """The quota is per domain, so the maximum runs over domains, not apps."""
    ctx = context()
    with Stubber(ctx.client('amplify')) as stub:
        stub_domains(stub, {'one': {'quiet.test': 1, 'busy.test': 4},
                            'two': {'other.test': 2}})
        result = check()(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'one/busy.test')
        stub.assert_no_pending_responses()


def test_a_domain_without_subdomains_counts_as_zero():
    ctx = context()
    with Stubber(ctx.client('amplify')) as stub:
        stub_domains(stub, {'one': {'bare.test': 0}})
        result = check()(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'one/bare.test')
        stub.assert_no_pending_responses()


def test_an_account_without_apps_counts_as_zero():
    ctx = context()
    with Stubber(ctx.client('amplify')) as stub:
        stub.add_response('list_apps', {'apps': []}, {})
        assert check()(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for a response the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_domain_without_a_name_is_reported():
    """The domain name is a required member, so only a broken response omits it."""
    ctx = FakeContext({'list_apps': [{'appId': 'one'}],
                       'list_domain_associations': [{'subDomains': []}]})
    with pytest.raises(NoData, match='name'):
        check()(ctx)
