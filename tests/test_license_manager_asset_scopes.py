"""License Manager asset scopes, read from listings the module already makes."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import license_manager
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'license-manager', 'QuotaCode': code,
                          'Value': 100}], account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in license_manager.CHECKS if quota == code)


def ruleset_arn(name):
    return f'arn:aws:license-manager:{REGION}:{ACCOUNT}:license-asset-ruleset/{name}'


def group_arn(name):
    return f'arn:aws:license-manager:{REGION}:{ACCOUNT}:license-asset-group/{name}'


def ruleset(name, rules):
    return {'Name': name, 'LicenseAssetRulesetArn': ruleset_arn(name),
            'Rules': [{'RuleStatement': {'InstanceRuleStatement': {}}}
                      for _ in range(rules)]}


def group(name, rulesets):
    return {'Name': name, 'LicenseAssetGroupArn': group_arn(name), 'Status': 'ACTIVE',
            'AssociatedLicenseAssetRulesetARNs': [ruleset_arn(f'r{index}')
                                                  for index in range(rulesets)]}


class FakeContext:
    """A context answering one listing, for responses the SDK cannot produce."""

    def __init__(self, items):
        self.items = items

    def call(self, _service, _method, _key, **_kwargs):
        return self.items


def test_the_ruleset_holding_the_most_rules_is_measured():
    ctx = context('L-A6872F54')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_rulesets', {'LicenseAssetRulesets': [
            ruleset('quiet', 2), ruleset('busy', 5)]}, {})
        result = check('L-A6872F54')(ctx)
        assert (result['usage'], result['resource_id']) == (5, ruleset_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_ruleset_stating_no_rule_counts_as_zero():
    """An empty ruleset still holds the quota, so it stays in the maximum."""
    ctx = context('L-A6872F54')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_rulesets',
                          {'LicenseAssetRulesets': [ruleset('bare', 0)]}, {})
        result = check('L-A6872F54')(ctx)
        assert (result['usage'], result['resource_id']) == (0, ruleset_arn('bare'))
        stub.assert_no_pending_responses()


def test_an_account_with_no_ruleset_counts_as_zero():
    ctx = context('L-A6872F54')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_rulesets',
                          {'LicenseAssetRulesets': []}, {})
        assert check('L-A6872F54')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_ruleset_without_an_arn_is_reported():
    """The ARN is a required member, so only a broken response omits it."""
    with pytest.raises(NoData, match='ARN'):
        check('L-A6872F54')(FakeContext([{'Name': 'nameless', 'Rules': []}]))


def test_the_group_associating_the_most_rulesets_is_measured():
    ctx = context('L-60C1FE55')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_groups', {'LicenseAssetGroups': [
            group('quiet', 1), group('busy', 4)]}, {})
        result = check('L-60C1FE55')(ctx)
        assert (result['usage'], result['resource_id']) == (4, group_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_group_associating_no_ruleset_counts_as_zero():
    ctx = context('L-60C1FE55')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_groups',
                          {'LicenseAssetGroups': [group('bare', 0)]}, {})
        result = check('L-60C1FE55')(ctx)
        assert (result['usage'], result['resource_id']) == (0, group_arn('bare'))
        stub.assert_no_pending_responses()


def test_a_group_without_an_arn_is_reported():
    """The ARN is a required member, so only a broken response omits it."""
    with pytest.raises(NoData, match='ARN'):
        check('L-60C1FE55')(FakeContext([{'Name': 'nameless'}]))


def test_the_new_scopes_reuse_the_listings_the_account_counts_already_make():
    """Each listing is read once per run, so the account count shares it."""
    ctx = context('L-9FC671A7')
    with Stubber(ctx.client('license-manager')) as stub:
        stub.add_response('list_license_asset_rulesets', {'LicenseAssetRulesets': [
            ruleset('one', 3), ruleset('two', 1)]}, {})
        assert check('L-9FC671A7')(ctx)['usage'] == 2
        assert check('L-A6872F54')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()
