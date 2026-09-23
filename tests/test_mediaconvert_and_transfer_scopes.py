"""MediaConvert queue occupancy and Transfer per-parent inventories."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import mediaconvert, transfer
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)
# Transfer validates these identifiers by length, so the fixtures use real shapes.
P_ONE, P_TWO = 'p-11111111111111111', 'p-22222222222222222'
S_MANAGED, S_DIRECTORY = 's-11111111111111111', 's-22222222222222222'
CERT = 'cert-1111111111111111111'


def server(server_id, provider):
    return {'ServerId': server_id, 'Domain': 'S3', 'EndpointType': 'PUBLIC',
            'Arn': f'arn:aws:transfer:eu-central-1:1:server/{server_id}',
            'IdentityProviderType': provider, 'State': 'ONLINE', 'UserCount': 0}


def user(name, keys):
    return {'Arn': f'arn:aws:transfer:eu-central-1:1:user/{name}', 'UserName': name,
            'SshPublicKeyCount': keys, 'Role': 'arn:aws:iam::1:role/transfer'}


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def queue(name, plan, progressing, kind='CUSTOM', slots=None):
    entry = {'Name': name, 'Arn': f'arn:q/{name}', 'PricingPlan': plan, 'Type': kind,
             'Status': 'ACTIVE', 'ProgressingJobsCount': progressing,
             'SubmittedJobsCount': 0, 'CreatedAt': MOMENT}
    if slots is not None:
        entry['ReservationPlan'] = {'ReservedSlots': slots, 'Commitment': 'ONE_YEAR',
                                    'RenewalType': 'EXPIRE', 'Status': 'ACTIVE'}
    return entry


QUEUES = [queue('Default', 'ON_DEMAND', 3, kind='SYSTEM'),
          queue('busy', 'ON_DEMAND', 7),
          queue('reserved', 'RESERVED', 2, slots=12)]


@pytest.mark.parametrize('code, expected', [
    ('L-89D4C825', 12),   # every queue's progressing jobs, summed
    ('L-1D14865F', 7),    # the busiest on-demand queue
    ('L-032C4FB4', 3),    # the default queue, which the API marks SYSTEM
    ('L-1AE7DAF9', 12),   # reserved slots on the reserved queue
])
def test_queue_occupancy_comes_from_the_queue_listing(code, expected):
    """ListQueues reports each queue's progressing jobs, so no job walk is needed."""
    ctx = context('mediaconvert', code)
    with Stubber(ctx.client('mediaconvert')) as stub:
        stub.add_response('list_queues', {'Queues': QUEUES}, {})
        assert check(code, mediaconvert.CHECKS)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def test_a_queue_without_a_progressing_count_is_reported():
    ctx = context('mediaconvert', 'L-89D4C825')
    with Stubber(ctx.client('mediaconvert')) as stub:
        bare = dict(QUEUES[1])
        del bare['ProgressingJobsCount']
        stub.add_response('list_queues', {'Queues': [bare]}, {})
        with pytest.raises(NoData, match='progressing'):
            check('L-89D4C825', mediaconvert.CHECKS)(ctx)


def test_an_account_without_a_reserved_queue_counts_no_slots():
    ctx = context('mediaconvert', 'L-1AE7DAF9')
    with Stubber(ctx.client('mediaconvert')) as stub:
        stub.add_response('list_queues', {'Queues': [QUEUES[0]]}, {})
        assert check('L-1AE7DAF9', mediaconvert.CHECKS)(ctx)['usage'] == 0


def test_only_custom_presets_count_against_the_custom_preset_quota():
    ctx = context('mediaconvert', 'L-8CFEB230')
    with Stubber(ctx.client('mediaconvert')) as stub:
        stub.add_response('list_presets', {'Presets': [
            {'Name': 'mine', 'Arn': 'arn:p/mine', 'Type': 'CUSTOM', 'Settings': {}},
            {'Name': 'theirs', 'Arn': 'arn:p/theirs', 'Type': 'SYSTEM', 'Settings': {}}]}, {})
        assert check('L-8CFEB230', mediaconvert.CHECKS)(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_certificates_are_counted_from_the_profile_detail():
    """The certificate listing does not say which profile holds a certificate."""
    ctx = context('transfer', 'L-B2750988')
    with Stubber(ctx.client('transfer')) as stub:
        stub.add_response('list_profiles', {'Profiles': [
            {'ProfileId': P_ONE, 'Arn': f'arn:aws:transfer:eu-central-1:1:profile/{P_ONE}',
             'As2Id': 'one', 'ProfileType': 'LOCAL'},
            {'ProfileId': P_TWO, 'Arn': f'arn:aws:transfer:eu-central-1:1:profile/{P_TWO}',
             'As2Id': 'two', 'ProfileType': 'PARTNER'}]}, {})
        stub.add_response('describe_profile', {'Profile': {
            'Arn': f'arn:aws:transfer:eu-central-1:1:profile/{P_ONE}', 'ProfileId': P_ONE,
            'CertificateIds': [CERT]}}, {'ProfileId': P_ONE})
        stub.add_response('describe_profile', {'Profile': {
            'Arn': f'arn:aws:transfer:eu-central-1:1:profile/{P_TWO}', 'ProfileId': P_TWO,
            'CertificateIds': [CERT, CERT, CERT]}}, {'ProfileId': P_TWO})
        result = check('L-B2750988', transfer.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, P_TWO)
        stub.assert_no_pending_responses()


def test_ssh_keys_are_counted_only_for_service_managed_servers():
    """A directory-backed server holds no service-managed users at all."""
    ctx = context('transfer', 'L-90797EDA')
    with Stubber(ctx.client('transfer')) as stub:
        stub.add_response('list_servers', {'Servers': [
            server(S_MANAGED, 'SERVICE_MANAGED'),
            server(S_DIRECTORY, 'AWS_DIRECTORY_SERVICE')]}, {})
        stub.add_response('list_users', {'ServerId': S_MANAGED, 'Users': [
            user('alice', 1), user('bob', 4)]}, {'ServerId': S_MANAGED})
        result = check('L-90797EDA', transfer.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (4, f'{S_MANAGED}:bob')
        stub.assert_no_pending_responses()


def test_directory_accesses_are_counted_per_server():
    ctx = context('transfer', 'L-843894CE')
    with Stubber(ctx.client('transfer')) as stub:
        stub.add_response('list_servers', {'Servers': [
            server(S_DIRECTORY, 'AWS_DIRECTORY_SERVICE')]}, {})
        stub.add_response('list_accesses', {'ServerId': S_DIRECTORY, 'Accesses': [
            {'ExternalId': 'S-1-5-21-1'}, {'ExternalId': 'S-1-5-21-2'}]},
            {'ServerId': S_DIRECTORY})
        assert check('L-843894CE', transfer.CHECKS)(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
