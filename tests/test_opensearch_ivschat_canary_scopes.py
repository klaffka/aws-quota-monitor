"""Three singletons whose services had no check of their own kind yet."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import misc_counts, opensearch
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def domain_check(code):
    return next(fn for quota, _name, fn in opensearch.DOMAIN_CHECKS if quota == code)


def misc_check(service, code):
    return next(fn for quota, _name, fn in misc_counts.CHECKS[service] if quota == code)


def stub_domains(stub, domains):
    """Stub the domain listing, then one describe for the whole batch.

    ``domains`` maps a domain name to its dedicated master count, or to None
    for a domain running no dedicated masters at all.
    """
    stub.add_response('list_domain_names', {'DomainNames': [
        {'DomainName': name} for name in domains]}, {})
    if not domains:
        return
    stub.add_response('describe_elasticsearch_domains', {'DomainStatusList': [
        {'DomainId': name, 'DomainName': name, 'ARN': f'arn:domain/{name}',
         'ElasticsearchClusterConfig': (
             {} if count is None else
             {'DedicatedMasterEnabled': True, 'DedicatedMasterCount': count})}
        for name, count in domains.items()]},
        {'DomainNames': list(domains)})


def test_the_domain_with_the_most_dedicated_masters_is_measured():
    ctx = context('es', 'L-AE676A72')
    with Stubber(ctx.client('es')) as stub:
        stub_domains(stub, {'quiet': 3, 'busy': 5})
        result = domain_check('L-AE676A72')(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'busy')
        stub.assert_no_pending_responses()


def test_a_domain_without_dedicated_masters_counts_as_zero():
    """A domain may run none, which is a real zero rather than a missing value."""
    ctx = context('es', 'L-AE676A72')
    with Stubber(ctx.client('es')) as stub:
        stub_domains(stub, {'plain': None})
        result = domain_check('L-AE676A72')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'plain')
        stub.assert_no_pending_responses()


def test_an_account_without_domains_counts_as_zero():
    """With no domain there is nothing to describe, so no batch call is made."""
    ctx = context('es', 'L-AE676A72')
    with Stubber(ctx.client('es')) as stub:
        stub_domains(stub, {})
        assert domain_check('L-AE676A72')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_domain_without_a_name_is_reported():
    ctx = context('es', 'L-AE676A72')
    with Stubber(ctx.client('es')) as stub:
        stub.add_response('list_domain_names', {'DomainNames': [{}]}, {})
        with pytest.raises(NoData, match='name'):
            domain_check('L-AE676A72')(ctx)


def test_chat_rooms_are_counted_from_the_listing():
    ctx = context('ivschat', 'L-85B84D18')
    with Stubber(ctx.client('ivschat')) as stub:
        stub.add_response('list_rooms', {'rooms': [
            {'arn': 'arn:room/one'}, {'arn': 'arn:room/two'}]}, {})
        result = misc_check('ivschat', 'L-85B84D18')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_an_account_without_chat_rooms_counts_as_zero():
    ctx = context('ivschat', 'L-85B84D18')
    with Stubber(ctx.client('ivschat')) as stub:
        stub.add_response('list_rooms', {'rooms': []}, {})
        assert misc_check('ivschat', 'L-85B84D18')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_canaries_are_counted_on_the_synthetics_client():
    """Service Quotas files the canary limit under CloudWatch; Synthetics owns it."""
    ctx = context('monitoring', 'L-C1FE0F5C')
    with Stubber(ctx.client('synthetics')) as stub:
        stub.add_response('describe_canaries', {'Canaries': [
            {'Name': 'one'}, {'Name': 'two'}, {'Name': 'three'}]}, {})
        result = misc_check('monitoring', 'L-C1FE0F5C')(ctx)
        assert (result['usage'], result['method']) == (3, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_an_account_without_canaries_counts_as_zero():
    ctx = context('monitoring', 'L-C1FE0F5C')
    with Stubber(ctx.client('synthetics')) as stub:
        stub.add_response('describe_canaries', {'Canaries': []}, {})
        assert misc_check('monitoring', 'L-C1FE0F5C')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()
