import json

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import sqs
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

BASE = 'https://sqs.eu-central-1.amazonaws.com/123456789012'
STANDARD = f'{BASE}/orders'
FIFO = f'{BASE}/events.fifo'


def context(code='L-4BE1B2BD'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'sqs', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def policy(statements):
    return json.dumps({'Version': '2012-10-17', 'Statement': statements})


def stub_queue(stub, url, attributes=None):
    stub.add_response('get_queue_attributes', {'Attributes': dict(
        {'QueueArn': f'arn:aws:sqs:eu-central-1:123456789012:{url.rsplit("/", 1)[-1]}'},
        **(attributes or {}))}, {'QueueUrl': url, 'AttributeNames': ['All']})


def check(code):
    return next(fn for quota, _, fn in sqs.CHECKS if quota == code)


def test_queue_name_length_measures_the_longest_name():
    ctx = context('L-E8A9C91E')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD, FIFO]}, {})
        result = sqs.queue_name_length(ctx)
        assert (result['usage'], result['resource_id']) == (len('events.fifo'), FIFO)
        stub.assert_no_pending_responses()


def test_in_flight_messages_ignore_fifo_queues():
    ctx = context('L-C491D5A4')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD, FIFO]}, {})
        stub_queue(stub, STANDARD, {'ApproximateNumberOfMessagesNotVisible': '7'})
        stub_queue(stub, FIFO, {'FifoQueue': 'true',
                                'ApproximateNumberOfMessagesNotVisible': '99'})
        result = sqs.in_flight_messages(ctx)
        # The FIFO queue has its own quota and must not win the maximum.
        assert (result['usage'], result['resource_id']) == (7, STANDARD)
        stub.assert_no_pending_responses()


def test_configured_attributes_report_the_largest_value():
    ctx = context('L-2DA3E3B2')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD, FIFO]}, {})
        stub_queue(stub, STANDARD, {'MessageRetentionPeriod': '345600'})
        stub_queue(stub, FIFO, {'MessageRetentionPeriod': '1209600'})
        result = check('L-2DA3E3B2')(ctx)
        assert (result['usage'], result['resource_id']) == (1209600, FIFO)
        stub.assert_no_pending_responses()


def test_a_missing_attribute_raises_nodata_instead_of_counting_zero():
    ctx = context('L-2DA3E3B2')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
        stub_queue(stub, STANDARD, {'VisibilityTimeout': '30'})
        with pytest.raises(NoData, match='message retention period'):
            check('L-2DA3E3B2')(ctx)


def test_policy_counts_cover_statements_actions_conditions_and_principals():
    document = policy([
        {'Effect': 'Allow', 'Principal': {'AWS': ['111122223333', '444455556666']},
         'Action': ['sqs:SendMessage', 'sqs:ReceiveMessage'], 'Resource': '*',
         'Condition': {'StringEquals': {'aws:SourceAccount': '1', 'aws:SourceArn': '2'}}},
        {'Effect': 'Deny', 'Principal': '*', 'Action': 'sqs:DeleteMessage',
         'Resource': '*'}])
    for code, expected in (('L-9F628B95', 2), ('L-79B6240C', 3),
                           ('L-6A03DCE9', 2), ('L-F61F33C3', 3)):
        ctx = context(code)
        with Stubber(ctx.client('sqs')) as stub:
            stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
            stub_queue(stub, STANDARD, {'Policy': document})
            assert check(code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_a_queue_without_a_policy_counts_as_zero():
    ctx = context('L-9F628B95')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
        stub_queue(stub, STANDARD, {'VisibilityTimeout': '30'})
        assert check('L-9F628B95')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_an_unparsable_policy_raises_nodata():
    ctx = context('L-9F628B95')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
        stub_queue(stub, STANDARD, {'Policy': 'not-json'})
        with pytest.raises(NoData, match='not valid JSON'):
            check('L-9F628B95')(ctx)


def test_policy_size_counts_utf8_bytes():
    document = policy([{'Effect': 'Allow', 'Principal': '*',
                        'Action': 'sqs:SendMessage', 'Resource': 'ü'}])
    ctx = context('L-BBEFA6CF')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
        stub_queue(stub, STANDARD, {'Policy': document})
        assert check('L-BBEFA6CF')(ctx)['usage'] == len(document.encode('utf-8'))
        stub.assert_no_pending_responses()


def test_tag_counts_and_utf8_lengths():
    tags = {'owner': 'team-a', 'kostenstelle': 'über-1234'}
    for code, expected in (('L-4BE1B2BD', 2), ('L-A01B4DF0', len('kostenstelle')),
                           ('L-BF2A6161', len('über-1234'.encode('utf-8')))):
        ctx = context(code)
        with Stubber(ctx.client('sqs')) as stub:
            stub.add_response('list_queues', {'QueueUrls': [STANDARD]}, {})
            # Tag checks never read queue attributes.
            stub.add_response('list_queue_tags', {'Tags': tags}, {'QueueUrl': STANDARD})
            assert check(code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_an_empty_account_reports_zero_rather_than_failing():
    ctx = context('L-E8A9C91E')
    with Stubber(ctx.client('sqs')) as stub:
        stub.add_response('list_queues', {}, {})
        result = sqs.queue_name_length(ctx)
        assert (result['usage'], result['resource_id']) == (0, None)
        stub.assert_no_pending_responses()


def test_every_sqs_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'sqs'}
    assert {code for code, _, _ in sqs.CHECKS} <= registered
