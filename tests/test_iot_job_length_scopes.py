"""IoT job and job template length quotas, all from calls already cached."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iot
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'iot', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in iot.CHECKS if quota == code)


def stub_job_listing(stub, job_ids):
    """The id scope reads the listing only, so no detail is queued."""
    stub.add_response('list_jobs', {'jobs': [
        {'jobId': identity, 'jobArn': f'arn:job/{identity}', 'status': 'COMPLETED'}
        for identity in job_ids]}, {})


def stub_jobs(stub, jobs):
    """Stub the job listing, then one detail per job.

    ``jobs`` maps a job id to ``(comment, description)``.
    """
    stub.add_response('list_jobs', {'jobs': [
        {'jobId': identity, 'jobArn': f'arn:job/{identity}', 'status': 'COMPLETED'}
        for identity in jobs]}, {})
    for identity, (comment, description) in jobs.items():
        job = {'jobId': identity, 'jobArn': f'arn:job/{identity}',
               'status': 'COMPLETED', 'targets': ['arn:thing/one']}
        if comment is not None:
            job['comment'] = comment
        if description is not None:
            job['description'] = description
        stub.add_response('describe_job', {'job': job}, {'jobId': identity})


def test_the_longest_job_id_is_measured():
    ctx = context('L-E41D2F60')
    with Stubber(ctx.client('iot')) as stub:
        stub_job_listing(stub, ['short', 'a-much-longer-job'])
        result = check('L-E41D2F60')(ctx)
        assert (result['usage'], result['resource_id']) == (17, 'a-much-longer-job')
        stub.assert_no_pending_responses()


def test_the_longest_job_comment_is_measured():
    ctx = context('L-3123807D')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'one': ('brief', None), 'two': ('a longer comment', None)})
        result = check('L-3123807D')(ctx)
        assert (result['usage'], result['resource_id']) == (16, 'two')
        stub.assert_no_pending_responses()


def test_a_job_without_a_comment_counts_as_zero():
    """A comment is optional, so its absence is a length of nothing."""
    ctx = context('L-3123807D')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'bare': (None, None)})
        result = check('L-3123807D')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


def test_the_longest_job_description_is_measured():
    ctx = context('L-94973834')
    with Stubber(ctx.client('iot')) as stub:
        stub_jobs(stub, {'one': (None, 'short'), 'two': (None, 'a longer one')})
        result = check('L-94973834')(ctx)
        assert (result['usage'], result['resource_id']) == (12, 'two')
        stub.assert_no_pending_responses()


def test_an_account_without_jobs_counts_as_zero():
    ctx = context('L-E41D2F60')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_jobs', {'jobs': []}, {})
        assert check('L-E41D2F60')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def stub_job_templates(stub, templates):
    """``templates`` maps a template id to its description, or to None."""
    stub.add_response('list_job_templates', {'jobTemplates': [
        {'jobTemplateId': identity, 'jobTemplateArn': f'arn:template/{identity}',
         **({} if description is None else {'description': description})}
        for identity, description in templates.items()]}, {})


def test_the_longest_job_template_id_is_measured():
    ctx = context('L-3470FAF6')
    with Stubber(ctx.client('iot')) as stub:
        stub_job_templates(stub, {'short': None, 'a-longer-template': None})
        result = check('L-3470FAF6')(ctx)
        assert (result['usage'], result['resource_id']) == (17, 'a-longer-template')
        stub.assert_no_pending_responses()


def test_the_longest_job_template_description_is_measured():
    """The listing already carries the description, so no detail is fetched."""
    ctx = context('L-CEAD881C')
    with Stubber(ctx.client('iot')) as stub:
        stub_job_templates(stub, {'one': 'brief', 'two': 'a longer description'})
        result = check('L-CEAD881C')(ctx)
        assert (result['usage'], result['resource_id']) == (20, 'two')
        stub.assert_no_pending_responses()


def test_a_job_template_without_a_description_counts_as_zero():
    ctx = context('L-CEAD881C')
    with Stubber(ctx.client('iot')) as stub:
        stub_job_templates(stub, {'bare': None})
        result = check('L-CEAD881C')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


def test_a_job_template_without_an_identity_is_reported():
    ctx = context('L-3470FAF6')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_job_templates', {'jobTemplates': [
            {'jobTemplateArn': 'arn:template/x'}]}, {})
        with pytest.raises(NoData, match='identity'):
            check('L-3470FAF6')(ctx)
