"""Transfer Family web app units, read from each web app's detail."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import transfer
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'
CODE = 'L-B51E8407'


def context(code=CODE):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'transfer', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code=CODE):
    return next(fn for quota, _name, fn in transfer.CHECKS if quota == code)


def web_app_id(name):
    """A web app id is at least 24 characters, so short names are padded."""
    return f'webapp-{name}'.ljust(24, '0')


def web_app_arn(identity):
    return f'arn:aws:transfer:{REGION}:{ACCOUNT}:webapp/{identity}'


def stub_web_apps(stub, apps):
    """Stub the web app listing, then one detail per app.

    ``apps`` maps a web app id to its provisioned units, or to None for an app
    whose detail states no units at all.
    """
    stub.add_response('list_web_apps', {'WebApps': [
        {'Arn': web_app_arn(web_app_id(name)), 'WebAppId': web_app_id(name)}
        for name in apps]}, {})
    for name, units in apps.items():
        identity = web_app_id(name)
        app = {'Arn': web_app_arn(identity), 'WebAppId': identity}
        if units is not None:
            app['WebAppUnits'] = {'Provisioned': units}
        stub.add_response('describe_web_app', {'WebApp': app},
                          {'WebAppId': identity})


def test_the_web_app_provisioning_the_most_units_is_measured():
    ctx = context()
    with Stubber(ctx.client('transfer')) as stub:
        stub_web_apps(stub, {'quiet': 1, 'busy': 6})
        result = check()(ctx)
        assert (result['usage'], result['resource_id']) == (6, web_app_id('busy'))
        stub.assert_no_pending_responses()


def test_an_account_without_web_apps_counts_as_zero():
    ctx = context()
    with Stubber(ctx.client('transfer')) as stub:
        stub_web_apps(stub, {})
        assert check()(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_web_app_stating_no_units_is_reported():
    """A web app always runs on units, so an absent count is not a zero."""
    ctx = context()
    with Stubber(ctx.client('transfer')) as stub:
        stub_web_apps(stub, {'odd': None})
        with pytest.raises(NoData, match='units'):
            check()(ctx)


class FakeContext:
    """A context answering one listing, for a response the SDK cannot produce."""

    def __init__(self, items):
        self.items = items

    def call(self, _service, _method, _key=None, **_kwargs):
        return self.items


def test_a_web_app_without_an_identity_is_reported():
    """The id is a required member, so only a broken response omits it."""
    with pytest.raises(NoData, match='identity'):
        check()(FakeContext([{'Arn': web_app_arn(web_app_id('x'))}]))
