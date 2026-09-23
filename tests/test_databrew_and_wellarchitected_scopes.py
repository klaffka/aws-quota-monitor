"""DataBrew ruleset scopes and Well-Architected share counts."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import databrew, wellarchitected
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 17, tzinfo=UTC)
# These shapes validate their identifiers by length, so the fixtures use real ones.
DATASET_ONE = 'arn:aws:databrew:eu-central-1:123456789012:dataset/one'
DATASET_TWO = 'arn:aws:databrew:eu-central-1:123456789012:dataset/two'
WORKLOAD_ONE, WORKLOAD_TWO = '1' * 32, '2' * 32
TEMPLATE_ONE = 'arn:aws:wellarchitected:eu-central-1:123456789012:review-template/one'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def ruleset(name, target, rules):
    return {'Name': name, 'TargetArn': target, 'RuleCount': rules}


RULESETS = {'Rulesets': [ruleset('strict', DATASET_ONE, 9),
                         ruleset('light', DATASET_ONE, 2),
                         ruleset('single', DATASET_TWO, 4)]}


def test_rules_and_rulesets_come_from_the_same_listing():
    """ListRulesets carries both the rule count and the dataset it targets."""
    ctx = context('databrew', 'L-640ABD4F')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_rulesets', RULESETS, {})
        result = check('L-640ABD4F', databrew.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (9, 'strict')
        stub.assert_no_pending_responses()


def test_rulesets_are_counted_against_the_dataset_they_target():
    ctx = context('databrew', 'L-131D2768')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_rulesets', RULESETS, {})
        result = check('L-131D2768', databrew.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, DATASET_ONE)
        stub.assert_no_pending_responses()


def test_a_ruleset_without_a_rule_count_is_reported():
    ctx = context('databrew', 'L-640ABD4F')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_rulesets',
                          {'Rulesets': [{'Name': 'bare', 'TargetArn': DATASET_ONE}]}, {})
        with pytest.raises(NoData, match='rule count'):
            check('L-640ABD4F', databrew.CHECKS)(ctx)


def test_only_projects_someone_has_open_count_as_open():
    """A project is open while DataBrew records who opened it."""
    ctx = context('databrew', 'L-5748848E')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_projects', {'Projects': [
            {'Name': 'live', 'RecipeName': 'r', 'OpenedBy': 'someone', 'OpenDate': MOMENT},
            {'Name': 'closed', 'RecipeName': 'r'}]}, {})
        result = check('L-5748848E', databrew.CHECKS)(ctx)
        assert (result['usage'], result['method']) == (1, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_recipe_versions_are_counted_per_recipe():
    ctx = context('databrew', 'L-A386FCB8')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_recipes', {'Recipes': [{'Name': 'deep'}, {'Name': 'flat'}]}, {})
        stub.add_response('list_recipe_versions', {'Recipes': [
            {'Name': 'deep', 'RecipeVersion': '1.0'},
            {'Name': 'deep', 'RecipeVersion': '2.0'}]}, {'Name': 'deep'})
        stub.add_response('list_recipe_versions', {'Recipes': [
            {'Name': 'flat', 'RecipeVersion': '1.0'}]}, {'Name': 'flat'})
        result = check('L-A386FCB8', databrew.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'deep')
        stub.assert_no_pending_responses()


def test_jobs_are_counted_for_the_account():
    ctx = context('databrew', 'L-0D2C4DFC')
    with Stubber(ctx.client('databrew')) as stub:
        stub.add_response('list_jobs', {'Jobs': [{'Name': 'one'}, {'Name': 'two'}]}, {})
        assert check('L-0D2C4DFC', databrew.CHECKS)(ctx)['usage'] == 2


def share(identity):
    return {'ShareId': identity, 'SharedWith': '123456789012', 'Status': 'ACCEPTED'}


def test_lens_shares_are_asked_for_only_on_lenses_this_account_owns():
    """A shared or AWS lens cannot be shared on again, so it holds no quota."""
    ctx = context('wellarchitected', 'L-E62A1DE4')
    with Stubber(ctx.client('wellarchitected')) as stub:
        stub.add_response('list_lenses', {'LensSummaries': [
            {'LensAlias': 'mine', 'LensArn': 'arn:lens/mine', 'LensName': 'Mine',
             'LensType': 'CUSTOM_SELF'}]}, {'LensType': 'CUSTOM_SELF'})
        stub.add_response('list_lens_shares',
                          {'LensShareSummaries': [share('s1'), share('s2')]},
                          {'LensAlias': 'mine'})
        result = check('L-E62A1DE4', wellarchitected.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'mine')
        stub.assert_no_pending_responses()


def test_workload_shares_are_counted_per_workload():
    ctx = context('wellarchitected', 'L-7E98904D')
    with Stubber(ctx.client('wellarchitected')) as stub:
        stub.add_response('list_workloads', {'WorkloadSummaries': [
            {'WorkloadId': WORKLOAD_ONE, 'WorkloadName': 'one'},
            {'WorkloadId': WORKLOAD_TWO, 'WorkloadName': 'two'}]}, {})
        stub.add_response('list_workload_shares',
                          {'WorkloadShareSummaries': [share('s1')]}, {'WorkloadId': WORKLOAD_ONE})
        stub.add_response('list_workload_shares',
                          {'WorkloadShareSummaries': []}, {'WorkloadId': WORKLOAD_TWO})
        result = check('L-7E98904D', wellarchitected.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (1, WORKLOAD_ONE)
        stub.assert_no_pending_responses()


def test_template_shares_are_counted_per_review_template():
    ctx = context('wellarchitected', 'L-A5DDC022')
    with Stubber(ctx.client('wellarchitected')) as stub:
        stub.add_response('list_review_templates', {'ReviewTemplates': [
            {'TemplateArn': TEMPLATE_ONE, 'TemplateName': 'one'}]}, {})
        stub.add_response('list_template_shares',
                          {'TemplateShareSummaries': [share('s1'), share('s2'), share('s3')]},
                          {'TemplateArn': TEMPLATE_ONE})
        result = check('L-A5DDC022', wellarchitected.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, TEMPLATE_ONE)
        stub.assert_no_pending_responses()
