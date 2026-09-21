"""Two period quotas that are stored configuration rather than a request bound."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import apigateway, iot
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def stub_jobs(stub, jobs):
    """``jobs`` maps a job id to its pre-signed URL lifetime, or to None."""
    stub.add_response('list_jobs', {'jobs': [
        {'jobId': identity, 'jobArn': f'arn:job/{identity}', 'status': 'COMPLETED'}
        for identity in jobs]}, {})
    for identity, expires in jobs.items():
        job = {'jobId': identity, 'jobArn': f'arn:job/{identity}',
               'status': 'COMPLETED', 'targets': ['arn:thing/one']}
        if expires is not None:
            job['presignedUrlConfig'] = {'roleArn': f'arn:aws:iam::{ACCOUNT}:role/signer',
                                         'expiresInSec': expires}
        stub.add_response('describe_job', {'job': job}, {'jobId': identity})


def test_the_longest_presigned_url_lifetime_is_measured():
    ctx = context('iot', 'L-FBBB476F')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'short': 900, 'long': 3600})
        result = check(iot, 'L-FBBB476F')(ctx)
        assert (result['usage'], result['resource_id']) == (3600, 'long')
        stub.assert_no_pending_responses()


def test_a_job_serving_no_presigned_url_counts_as_zero():
    """A job whose document is inline signs no URL, so it configures no lifetime."""
    ctx = context('iot', 'L-FBBB476F')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'inline': None})
        result = check(iot, 'L-FBBB476F')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'inline')
        stub.assert_no_pending_responses()


def test_the_lifetime_rides_the_detail_the_target_count_already_fetches():
    """Both quotas read one describe per job, made once per run."""
    ctx = context('iot', 'L-9D1E0A0D')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'one': 1800})
        assert check(iot, 'L-FBBB476F')(ctx)['usage'] == 1800
        assert check(iot, 'L-9D1E0A0D')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def stub_stages(stub, stages):
    """``stages`` maps a stage name to its method-setting cache TTLs."""
    stub.add_response('get_rest_apis', {'items': [{'id': 'api', 'name': 'api'}]}, {})
    stub.add_response('get_stages', {'item': [
        {'stageName': name, 'methodSettings': {
            f'~1resource{index}/GET': {'cacheTtlInSeconds': ttl}
            for index, ttl in enumerate(ttls)}}
        for name, ttls in stages.items()]}, {'restApiId': 'api'})


def test_the_longest_cache_ttl_is_measured():
    ctx = context('apigateway', 'L-8C2F9A1D')
    with Stubber(ctx.client('apigateway')) as stub:
        stub_stages(stub, {'test': [30], 'prod': [300, 3600]})
        result = check(apigateway, 'L-8C2F9A1D')(ctx)
        assert (result['usage'], result['resource_id']) == (3600, 'api/prod')
        stub.assert_no_pending_responses()


def test_a_stage_caching_nothing_counts_as_zero():
    ctx = context('apigateway', 'L-8C2F9A1D')
    with Stubber(ctx.client('apigateway')) as stub:
        stub_stages(stub, {'plain': []})
        result = check(apigateway, 'L-8C2F9A1D')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'api/plain')
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for a response the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_stage_with_an_invalid_method_setting_is_reported():
    ctx = FakeContext({'get_rest_apis': [{'id': 'api'}],
                       'get_stages': [{'stageName': 'prod',
                                       'methodSettings': ['not-a-map']}]})
    with pytest.raises(NoData, match='method setting'):
        check(apigateway, 'L-8C2F9A1D')(ctx)
