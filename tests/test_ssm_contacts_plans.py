"""Incident Manager engagement plans, stages and rotations."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ssm_contacts
from modules.qmcore.aws import CheckContext, NoData


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ssm-contacts', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in ssm_contacts.CHECKS if quota == code)


CONTACTS = ['arn:aws:ssm-contacts:eu-central-1:123456789012:contact/one',
            'arn:aws:ssm-contacts:eu-central-1:123456789012:contact/two']
PLANS = {
    CONTACTS[0]: [{'DurationInMinutes': 5, 'Targets': [{'ChannelTargetInfo':
                   {'ContactChannelId': 'c1'}}]}],
    CONTACTS[1]: [{'DurationInMinutes': 5, 'Targets': [
                       {'ChannelTargetInfo': {'ContactChannelId': 'c2'}},
                       {'ChannelTargetInfo': {'ContactChannelId': 'c3'}}]},
                  {'DurationInMinutes': 5, 'Targets': []}]}


def stub_contacts(stub):
    stub.add_response('list_contacts', {'Contacts': [
        {'ContactArn': arn, 'Alias': f'alias{index}', 'Type': 'PERSONAL'}
        for index, arn in enumerate(CONTACTS)]}, {})
    for arn, stages in PLANS.items():
        stub.add_response('get_contact', {
            'ContactArn': arn, 'Alias': 'alias', 'Type': 'PERSONAL',
            'Plan': {'Stages': stages}}, {'ContactId': arn})


def test_stages_use_the_contact_with_the_longest_plan():
    ctx = context('L-5AE11799')
    with Stubber(ctx.client('ssm-contacts')) as stub:
        stub_contacts(stub)
        result = check('L-5AE11799')(ctx)
        assert (result['usage'], result['resource_id']) == (2, CONTACTS[1])
        stub.assert_no_pending_responses()


def test_channels_use_the_widest_stage_not_the_widest_contact():
    """A contact with two thin stages must not outrank one wide stage."""
    ctx = context('L-F338226A')
    with Stubber(ctx.client('ssm-contacts')) as stub:
        stub_contacts(stub)
        result = check('L-F338226A')(ctx)
        assert (result['usage'], result['resource_id']) == (2, f'{CONTACTS[1]}#0')
        stub.assert_no_pending_responses()


def test_contacts_use_the_largest_rotation():
    ctx = context('L-D438A616')
    with Stubber(ctx.client('ssm-contacts')) as stub:
        stub.add_response('list_rotations', {'Rotations': [
            {'RotationArn': 'arn:rotation/small', 'Name': 'small', 'ContactIds': ['a']},
            {'RotationArn': 'arn:rotation/large', 'Name': 'large',
             'ContactIds': ['a', 'b', 'c']}]}, {})
        result = check('L-D438A616')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'arn:rotation/large')
        stub.assert_no_pending_responses()


def test_a_contact_detail_for_another_contact_is_refused():
    ctx = context('L-5AE11799')
    with Stubber(ctx.client('ssm-contacts')) as stub:
        stub.add_response('list_contacts', {'Contacts': [
            {'ContactArn': CONTACTS[0], 'Alias': 'one', 'Type': 'PERSONAL'}]}, {})
        stub.add_response('get_contact', {'ContactArn': CONTACTS[1], 'Alias': 'two',
                                          'Type': 'PERSONAL', 'Plan': {'Stages': []}},
                          {'ContactId': CONTACTS[0]})
        with pytest.raises(NoData, match='different identity'):
            check('L-5AE11799')(ctx)
