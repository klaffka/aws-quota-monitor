import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ivs
from modules.qmcore.aws import CheckContext, NoData

STAGE = 'arn:aws:ivs:eu-central-1:123456789012:stage/abcdefghij'
CHANNEL = 'arn:aws:ivs:eu-central-1:123456789012:channel/abcdefghij'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ivs', 'QuotaCode': code, 'Value': 10}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in ivs.CHECKS if candidate == code)


def composition(arn, stage, state, destinations=1):
    return {'arn': arn, 'stageArn': stage, 'state': state,
            'destinations': [{'id': str(index), 'state': 'ACTIVE'}
                             for index in range(destinations)]}


def test_stopped_compositions_no_longer_hold_capacity():
    ctx = context('L-E945C199')
    with Stubber(ctx.client('ivs-realtime')) as stub:
        stub.add_response('list_compositions', {'compositions': [
            composition('c1', STAGE, 'ACTIVE'),
            composition('c2', STAGE, 'STARTING'),
            composition('c3', STAGE, 'STOPPED')]}, {})
        assert check('L-E945C199')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_compositions_and_destinations_are_reported_per_resource():
    ctx = context('L-21B2923F')
    other = STAGE.replace('abcdefghij', 'klmnopqrst')
    with Stubber(ctx.client('ivs-realtime')) as stub:
        stub.add_response('list_compositions', {'compositions': [
            composition('c1', STAGE, 'ACTIVE', destinations=1),
            composition('c2', STAGE, 'ACTIVE', destinations=3),
            composition('c3', other, 'ACTIVE', destinations=2)]}, {})
        per_stage = check('L-21B2923F')(ctx)
        assert (per_stage['usage'], per_stage['resource_id']) == (2, STAGE)
        # The inventory is cached, so the second check needs no further call.
        per_composition = check('L-9C6AF7E0')(ctx)
        assert (per_composition['usage'], per_composition['resource_id']) == (3, 'c2')
        stub.assert_no_pending_responses()


def test_an_unknown_composition_state_raises_nodata():
    ctx = context('L-E945C199')
    with Stubber(ctx.client('ivs-realtime')) as stub:
        stub.add_response('list_compositions', {'compositions': [
            composition('c1', STAGE, 'PAUSED')]}, {})
        with pytest.raises(NoData, match='unknown state'):
            check('L-E945C199')(ctx)


def test_stream_keys_report_the_fullest_channel():
    ctx = context('L-80F95143')
    other = CHANNEL.replace('abcdefghij', 'klmnopqrst')
    with Stubber(ctx.client('ivs')) as stub:
        stub.add_response('list_channels', {'channels': [
            {'arn': CHANNEL}, {'arn': other}]}, {})
        stub.add_response('list_stream_keys', {'streamKeys': [{'arn': 'k1'}]},
                          {'channelArn': CHANNEL})
        stub.add_response('list_stream_keys',
                          {'streamKeys': [{'arn': 'k2'}, {'arn': 'k3'}]},
                          {'channelArn': other})
        result = check('L-80F95143')(ctx)
        assert (result['usage'], result['resource_id']) == (2, other)
        stub.assert_no_pending_responses()


def test_only_connected_publishers_of_the_active_session_are_counted():
    ctx = context('L-9965E8BE')
    idle = STAGE.replace('abcdefghij', 'klmnopqrst')
    with Stubber(ctx.client('ivs-realtime')) as stub:
        stub.add_response('list_stages', {'stages': [
            {'arn': STAGE, 'activeSessionId': 'st-abcdefghijklmn'}, {'arn': idle}]}, {})
        stub.add_response('list_participants', {'participants': [
            {'participantId': 'p1', 'state': 'CONNECTED', 'published': True},
            {'participantId': 'p2', 'state': 'DISCONNECTED', 'published': True}]},
            {'stageArn': STAGE, 'sessionId': 'st-abcdefghijklmn', 'filterByPublished': True})
        result = check('L-9965E8BE')(ctx)
        assert (result['usage'], result['resource_id']) == (1, STAGE)
        stub.assert_no_pending_responses()


def test_the_plain_inventories_count_their_own_lists():
    ctx = context('L-47F0B706')
    with Stubber(ctx.client('ivs-realtime')) as realtime, \
            Stubber(ctx.client('ivs')) as core:
        realtime.add_response('list_stages', {'stages': [{'arn': STAGE}]}, {})
        realtime.add_response('list_public_keys',
                              {'publicKeys': [{'arn': 'k1'}, {'arn': 'k2'}]}, {})
        core.add_response('list_ad_configurations', {'adConfigurations': [
            {'arn': 'a1', 'mediaTailorPlaybackConfigurations': [{'playbackConfigurationArn': 'arn:aws:mediatailor:eu-central-1:123456789012:playbackConfiguration/one'}]}]}, {})
        assert check('L-47F0B706')(ctx)['usage'] == 1
        assert check('L-DA157FF6')(ctx)['usage'] == 2
        assert check('L-D15E1F21')(ctx)['usage'] == 1
        realtime.assert_no_pending_responses()
        core.assert_no_pending_responses()
