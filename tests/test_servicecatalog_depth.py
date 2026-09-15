import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import servicecatalog
from modules.qmcore.aws import CheckContext, NoData

PORTFOLIO = 'port-1111111111111'
OTHER_PORTFOLIO = 'port-2222222222222'
PRODUCT = 'prod-1111111111111'
APPLICATION = '0aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'servicecatalog', 'QuotaCode': code,
                          'Value': 100}], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in servicecatalog.CHECKS if candidate == code)


def portfolio(identity):
    return {'Id': identity, 'DisplayName': identity, 'ProviderName': 'team'}


def product(identity):
    return {'ProductViewSummary': {'ProductId': identity, 'Name': identity},
            'Status': 'AVAILABLE'}


def test_portfolio_shares_and_principals_are_reported_per_portfolio():
    ctx = context('L-A2FB1BD2')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('list_portfolios', {'PortfolioDetails': [
            portfolio(PORTFOLIO), portfolio(OTHER_PORTFOLIO)]}, {})
        stub.add_response('list_portfolio_access',
                          {'AccountIds': ['111111111111', '222222222222']},
                          {'PortfolioId': PORTFOLIO})
        stub.add_response('list_portfolio_access', {'AccountIds': ['333333333333']},
                          {'PortfolioId': OTHER_PORTFOLIO})
        result = check('L-A2FB1BD2')(ctx)
        assert (result['usage'], result['resource_id']) == (2, PORTFOLIO)
        stub.assert_no_pending_responses()


def test_portfolio_access_is_read_beyond_its_first_page():
    """ListPortfolioAccess has no paginator and returns NextPageToken."""
    ctx = context('L-A2FB1BD2')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('list_portfolios',
                          {'PortfolioDetails': [portfolio(PORTFOLIO)]}, {})
        stub.add_response('list_portfolio_access',
                          {'AccountIds': ['111111111111'], 'NextPageToken': 'next'},
                          {'PortfolioId': PORTFOLIO})
        stub.add_response('list_portfolio_access', {'AccountIds': ['222222222222']},
                          {'PortfolioId': PORTFOLIO, 'PageToken': 'next'})
        assert check('L-A2FB1BD2')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_versions_and_service_actions_are_read_per_product_and_artifact():
    ctx = context('L-A5846085')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('search_products_as_admin',
                          {'ProductViewDetails': [product(PRODUCT)]}, {})
        stub.add_response('list_provisioning_artifacts', {
            'ProvisioningArtifactDetails': [{'Id': 'pa-1'}, {'Id': 'pa-2'}]},
            {'ProductId': PRODUCT})
        versions = check('L-A5846085')(ctx)
        assert (versions['usage'], versions['resource_id']) == (2, PRODUCT)
        stub.add_response('list_service_actions_for_provisioning_artifact',
                          {'ServiceActionSummaries': [{'Id': 'act-1'}]},
                          {'ProductId': PRODUCT, 'ProvisioningArtifactId': 'pa-1'})
        stub.add_response('list_service_actions_for_provisioning_artifact',
                          {'ServiceActionSummaries': []},
                          {'ProductId': PRODUCT, 'ProvisioningArtifactId': 'pa-2'})
        actions = check('L-58FC5582')(ctx)
        assert (actions['usage'], actions['resource_id']) == (1, f'{PRODUCT}/pa-1')
        stub.assert_no_pending_responses()


def test_tags_and_tag_options_come_from_the_describe_calls():
    ctx = context('L-77FEF8C5')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('list_portfolios',
                          {'PortfolioDetails': [portfolio(PORTFOLIO)]}, {})
        stub.add_response('describe_portfolio', {
            'PortfolioDetail': {'Id': PORTFOLIO},
            'Tags': [{'Key': 'a', 'Value': '1'}, {'Key': 'b', 'Value': '2'}],
            'TagOptions': [{'Key': 'c', 'Value': '3', 'Id': 'tag-1'}]},
            {'Id': PORTFOLIO})
        tags = check('L-77FEF8C5')(ctx)
        assert (tags['usage'], tags['resource_id']) == (2, PORTFOLIO)
        stub.add_response('search_products_as_admin',
                          {'ProductViewDetails': [product(PRODUCT)]}, {})
        stub.add_response('describe_product_as_admin', {
            'ProductViewDetail': {'Status': 'AVAILABLE'},
            'Tags': [{'Key': 'a', 'Value': '1'}],
            'TagOptions': [{'Key': 'c', 'Value': '3', 'Id': 'tag-1'},
                           {'Key': 'd', 'Value': '4', 'Id': 'tag-2'}]},
            {'Id': PRODUCT})
        options = check('L-73A88F28')(ctx)
        assert (options['usage'], options['resource_id']) == (2, PRODUCT)
        stub.assert_no_pending_responses()


def test_tag_option_values_are_grouped_by_key():
    ctx = context('L-79127A24')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('list_tag_options', {'TagOptionDetails': [
            {'Key': 'env', 'Value': 'dev', 'Id': 'tag-1'},
            {'Key': 'env', 'Value': 'prod', 'Id': 'tag-2'},
            {'Key': 'team', 'Value': 'core', 'Id': 'tag-3'}]}, {})
        result = check('L-79127A24')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'env')
        stub.assert_no_pending_responses()


def test_a_tag_option_without_a_key_raises_nodata():
    ctx = context('L-79127A24')
    with Stubber(ctx.client('servicecatalog')) as stub:
        stub.add_response('list_tag_options',
                          {'TagOptionDetails': [{'Value': 'dev', 'Id': 'tag-1'}]}, {})
        with pytest.raises(NoData, match='missing its key'):
            check('L-79127A24')(ctx)


def test_appregistry_inventories_are_reported_per_application():
    ctx = context('L-360CDF2E')
    with Stubber(ctx.client('servicecatalog-appregistry')) as stub:
        stub.add_response('list_applications', {'applications': [
            {'id': APPLICATION, 'name': 'one'}]}, {})
        stub.add_response('list_associated_resources', {'resources': [
            {'name': 'one', 'arn': 'arn:aws:s3:::bucket'},
            {'name': 'two', 'arn': 'arn:aws:s3:::other'}]}, {'application': APPLICATION})
        result = check('L-360CDF2E')(ctx)
        assert (result['usage'], result['resource_id']) == (2, APPLICATION)
        stub.add_response('list_attribute_groups', {'attributeGroups': [
            {'id': APPLICATION, 'name': 'group'}]}, {})
        assert check('L-1639038A')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
