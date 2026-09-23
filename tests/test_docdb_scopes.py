"""DocumentDB account inventories and per-cluster scopes."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import docdb
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 17, tzinfo=UTC)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'docdb', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in docdb.CHECKS if quota == code)


def cluster(identity, replicas):
    members = [{'DBInstanceIdentifier': f'{identity}-writer', 'IsClusterWriter': True}]
    members += [{'DBInstanceIdentifier': f'{identity}-reader-{index}',
                 'IsClusterWriter': False} for index in range(replicas)]
    return {'DBClusterIdentifier': identity, 'Engine': 'docdb',
            'DBClusterMembers': members}


def test_read_replicas_exclude_the_writer_each_cluster_has():
    """Every cluster has a writer, so counting members would be one too many."""
    ctx = context('L-5BA57179')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_clusters', {'DBClusters': [
            cluster('busy', 3), cluster('quiet', 1)]}, {})
        result = check('L-5BA57179')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'busy')
        stub.assert_no_pending_responses()


def test_a_cluster_with_only_a_writer_counts_as_zero_replicas():
    ctx = context('L-5BA57179')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_clusters', {'DBClusters': [cluster('lonely', 0)]}, {})
        assert check('L-5BA57179')(ctx)['usage'] == 0


def test_only_manual_snapshots_count_against_the_manual_quota():
    """AWS filters by snapshot type server side, so automated ones never load."""
    ctx = context('L-B2551F83')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_cluster_snapshots', {'DBClusterSnapshots': [
            {'DBClusterSnapshotIdentifier': 'one', 'SnapshotType': 'manual'},
            {'DBClusterSnapshotIdentifier': 'two', 'SnapshotType': 'manual'}]},
            {'SnapshotType': 'manual'})
        result = check('L-B2551F83')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_subnets_are_counted_per_subnet_group():
    ctx = context('L-36C7F3F8')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_subnet_groups', {'DBSubnetGroups': [
            {'DBSubnetGroupName': 'wide',
             'Subnets': [{'SubnetIdentifier': 'subnet-1'}, {'SubnetIdentifier': 'subnet-2'}]},
            {'DBSubnetGroupName': 'narrow', 'Subnets': [{'SubnetIdentifier': 'subnet-3'}]}]}, {})
        result = check('L-36C7F3F8')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'wide')
        stub.assert_no_pending_responses()


def test_security_groups_are_counted_per_instance():
    ctx = context('L-D02D85EA')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_instances', {'DBInstances': [
            {'DBInstanceIdentifier': 'guarded', 'VpcSecurityGroups': [
                {'VpcSecurityGroupId': 'sg-1'}, {'VpcSecurityGroupId': 'sg-2'}]},
            {'DBInstanceIdentifier': 'plain', 'VpcSecurityGroups': [
                {'VpcSecurityGroupId': 'sg-3'}]}]}, {})
        result = check('L-D02D85EA')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'guarded')
        stub.assert_no_pending_responses()


def test_a_cluster_without_an_identity_is_reported():
    ctx = context('L-5BA57179')
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response('describe_db_clusters',
                          {'DBClusters': [{'Engine': 'docdb', 'DBClusterMembers': []}]}, {})
        with pytest.raises(NoData, match='identity'):
            check('L-5BA57179')(ctx)


@pytest.mark.parametrize('code, method, key', [
    ('L-2A542E16', 'describe_db_cluster_parameter_groups', 'DBClusterParameterGroups'),
    ('L-F7FABF71', 'describe_event_subscriptions', 'EventSubscriptionsList'),
])
def test_the_account_inventories_are_plain_counts(code, method, key):
    ctx = context(code)
    with Stubber(ctx.client('docdb')) as stub:
        stub.add_response(method, {key: [{}, {}, {}]}, {})
        assert check(code)(ctx)['usage'] == 3
        stub.assert_no_pending_responses()
