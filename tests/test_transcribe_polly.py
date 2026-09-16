from unittest.mock import Mock

from modules.qmchecks.polly import CHECKS as POLLY_CHECKS
from modules.qmchecks.transcribe import CHECKS as TRANSCRIBE_CHECKS


# The plain regional inventories; the job and vocabulary state checks filter
# server side and are covered by their own tests below.
COUNTED = {'L-3278D334', 'L-CB43679D', 'L-79BBEFC1', 'L-68305688', 'L-BE7BEF67',
           'L-9190489D', 'L-866105CB', 'L-E3EBEDF2'}


def test_transcribe_checks_use_paginated_resource_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert all(check(ctx)['usage'] == 2 for code, _, check in TRANSCRIBE_CHECKS
               if code in COUNTED)


def test_polly_counts_lexicons():
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'one'}, {'Name': 'two'}]
    assert POLLY_CHECKS[0][2](ctx)['usage'] == 2


def transcribe_check(code):
    return next(fn for quota, _, fn in TRANSCRIBE_CHECKS if quota == code)


def test_running_jobs_ask_transcribe_for_each_unfinished_status():
    import boto3
    from botocore.stub import Stubber
    from modules.qmcore.aws import CheckContext

    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       [{'ServiceCode': 'transcribe', 'QuotaCode': 'L-58D7221C',
                         'Value': 100}], account='123456789012')
    with Stubber(ctx.client('transcribe')) as stub:
        stub.add_response('list_transcription_jobs', {'TranscriptionJobSummaries': [
            {'TranscriptionJobName': 'a', 'TranscriptionJobStatus': 'QUEUED'}]},
            {'Status': 'QUEUED'})
        stub.add_response('list_transcription_jobs', {'TranscriptionJobSummaries': [
            {'TranscriptionJobName': 'b', 'TranscriptionJobStatus': 'IN_PROGRESS'},
            {'TranscriptionJobName': 'c', 'TranscriptionJobStatus': 'IN_PROGRESS'}]},
            {'Status': 'IN_PROGRESS'})
        assert transcribe_check('L-58D7221C')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_rules_are_counted_per_call_analytics_category():
    import boto3
    from botocore.stub import Stubber
    from modules.qmchecks.transcribe import rules_per_category
    from modules.qmcore.aws import CheckContext

    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       [{'ServiceCode': 'transcribe', 'QuotaCode': 'L-2E269322',
                         'Value': 20}], account='123456789012')
    with Stubber(ctx.client('transcribe')) as stub:
        stub.add_response('list_call_analytics_categories', {'Categories': [
            {'CategoryName': 'escalation', 'Rules': [
                {'NonTalkTimeFilter': {'Threshold': 10}},
                {'InterruptionFilter': {'Threshold': 5}}]},
            {'CategoryName': 'quiet', 'Rules': [
                {'NonTalkTimeFilter': {'Threshold': 60}}]}]}, {})
        result = rules_per_category(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'escalation')
        stub.assert_no_pending_responses()
