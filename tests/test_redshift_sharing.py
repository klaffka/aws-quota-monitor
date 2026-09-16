import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import redshift
from modules.qmcore.aws import CheckContext, NoData

KEY = 'arn:aws:kms:eu-central-1:123456789012:key/11111111-1111-1111-1111-111111111111'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'redshift', 'QuotaCode': code, 'Value': 20}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in redshift.CHECKS if candidate == code)


def snapshot(identity, key, accounts):
    return {'SnapshotIdentifier': identity, 'KmsKeyId': key,
            'AccountsWithRestoreAccess': [{'AccountId': account}
                                          for account in accounts]}


def test_restore_access_is_reported_per_snapshot_and_per_key():
    ctx = context('L-909949E5')
    with Stubber(ctx.client('redshift')) as stub:
        stub.add_response('describe_cluster_snapshots', {'Snapshots': [
            snapshot('snap-a', KEY, ['111111111111', '222222222222']),
            snapshot('snap-b', KEY, ['222222222222', '333333333333']),
            snapshot('snap-c', KEY + '-2', ['111111111111'])]}, {})
        per_snapshot = check('L-909949E5')(ctx)
        assert (per_snapshot['usage'], per_snapshot['resource_id']) == (2, 'snap-a')
        # The same account on two snapshots of one key is one authorisation.
        per_key = check('L-7097B286')(ctx)
        assert (per_key['usage'], per_key['resource_id']) == (3, KEY)
        stub.assert_no_pending_responses()


def test_a_shared_account_without_an_id_raises_nodata():
    ctx = context('L-7097B286')
    with Stubber(ctx.client('redshift')) as stub:
        stub.add_response('describe_cluster_snapshots', {'Snapshots': [
            {'SnapshotIdentifier': 'snap-a', 'KmsKeyId': KEY,
             'AccountsWithRestoreAccess': [{}]}]}, {})
        with pytest.raises(NoData, match='without an ID'):
            check('L-7097B286')(ctx)


def test_subnets_are_reported_for_the_fullest_group():
    ctx = context('L-6C6B6042')
    with Stubber(ctx.client('redshift')) as stub:
        stub.add_response('describe_cluster_subnet_groups', {'ClusterSubnetGroups': [
            {'ClusterSubnetGroupName': 'one',
             'Subnets': [{'SubnetIdentifier': 'subnet-1'}]},
            {'ClusterSubnetGroupName': 'two',
             'Subnets': [{'SubnetIdentifier': 'subnet-2'},
                         {'SubnetIdentifier': 'subnet-3'}]}]}, {})
        result = check('L-6C6B6042')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'two')
        stub.assert_no_pending_responses()


def test_event_subscriptions_and_reserved_nodes_are_counted():
    ctx = context('L-2B30DCFE')
    with Stubber(ctx.client('redshift')) as stub:
        stub.add_response('describe_event_subscriptions', {'EventSubscriptionsList': [
            {'CustSubscriptionId': 'one'}, {'CustSubscriptionId': 'two'}]}, {})
        stub.add_response('describe_reserved_nodes', {'ReservedNodes': [
            {'ReservedNodeId': 'one'}]}, {})
        assert check('L-2B30DCFE')(ctx)['usage'] == 2
        assert check('L-58C8C0E8')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
