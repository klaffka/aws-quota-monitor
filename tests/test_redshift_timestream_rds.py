from unittest.mock import Mock

from modules.qmchecks.rds_resources import CHECKS as RDS_CHECKS
from modules.qmchecks.redshift import nodes_per_cluster, total_nodes
from modules.qmchecks.timestream import CHECKS as TIMESTREAM_CHECKS
from modules.qmchecks.redshift import CHECKS as REDSHIFT_CHECKS


def test_redshift_node_counts_are_account_total_and_cluster_maximum():
    ctx = Mock()
    ctx.call.return_value = [
        {'ClusterIdentifier': 'one', 'NumberOfNodes': 2},
        {'ClusterIdentifier': 'two', 'NumberOfNodes': 4},
    ]
    assert total_nodes(ctx)['usage'] == 6
    result = nodes_per_cluster(ctx)
    assert (result['usage'], result['resource_id']) == (4, 'two')


def test_timestream_checks_have_expected_resource_counts():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert TIMESTREAM_CHECKS[0][2](ctx)['usage'] == 2
    assert TIMESTREAM_CHECKS[2][2](ctx)['usage'] == 2


def test_rds_resource_checks_use_paginated_api_keys():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    parent = {'L-9372BAB3', 'L-5BC124EF', 'L-6F3ACC36', 'L-AA8B1026', 'L-7ADDB58A',
              'L-A399AC0B', 'L-DD2301CA', 'L-E094F43D'}
    assert all(check(ctx)['usage'] == 2 for code, _, check in RDS_CHECKS if code not in parent)


def test_rds_parent_scoped_maxima_use_inventory_fields():
    from modules.qmchecks.rds_resources import read_replicas_per_primary, subnets_per_subnet_group
    ctx = Mock()
    ctx.call.side_effect = [
        [{'DBInstanceIdentifier': 'replica', 'ReadReplicaSourceDBInstanceIdentifier': 'primary'},
         {'DBInstanceIdentifier': 'replica-2', 'ReadReplicaSourceDBInstanceIdentifier': 'primary'}],
        [{'DBSubnetGroupName': 'group', 'Subnets': [{}, {}]}],
    ]
    assert read_replicas_per_primary(ctx)['usage'] == 2
    assert subnets_per_subnet_group(ctx)['usage'] == 2


def test_rds_storage_sums_allocated_gb():
    from modules.qmchecks.rds_resources import total_storage
    ctx = Mock()
    ctx.call.return_value = [{'AllocatedStorage': 20}, {'AllocatedStorage': 30}]
    result = total_storage(ctx)
    assert (result['usage'], result['unit']) == (50, 'GB')


def test_rds_custom_engine_versions_filter_custom_engines():
    from modules.qmchecks.rds_resources import custom_engine_versions
    ctx = Mock()
    ctx.call.return_value = [
        {'Engine': 'custom-oracle-ee'}, {'Engine': 'postgres'}, {'Engine': 'custom-sqlserver-ee'}]
    assert custom_engine_versions(ctx)['usage'] == 2


def test_rds_iam_roles_use_maximum_per_instance_or_cluster():
    from modules.qmchecks.rds_resources import iam_roles_per_parent
    ctx = Mock()
    ctx.call.return_value = [
        {'DBInstanceIdentifier': 'one', 'AssociatedRoles': [{}]},
        {'DBInstanceIdentifier': 'two', 'AssociatedRoles': [{}, {}]},
    ]
    result = iam_roles_per_parent(ctx, 'describe_db_instances', 'DBInstances',
                                  'DBInstanceIdentifier', 'DBInstance')
    assert (result['usage'], result['resource_id']) == (2, 'two')


def test_rds_snapshot_and_shard_group_checks_have_distinct_quota_codes():
    codes = {code for code, _, _ in RDS_CHECKS}
    assert {'L-272F1212', 'L-9B510759', 'L-75AC651F'} <= codes
    assert {'L-9372BAB3', 'L-A59F4C87'} <= codes


def test_redshift_inventory_checks_use_account_resource_apis():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    # The node check expects NumberOfNodes, while inventory checks count pages.
    ctx.call.return_value = [{'NumberOfNodes': 1, 'NodeType': 'ra3.xlplus'}, {'NumberOfNodes': 2, 'NodeType': 'ra3.4xlarge'}]
    count_codes = {'L-BB966966', 'L-93AC8AE6', 'L-890444C0',
                   'L-2E428669', 'L-A3830BB3', 'L-BE12F428'}
    assert [check(ctx)['usage'] for code, _, check in REDSHIFT_CHECKS if code in count_codes] == [2] * len(count_codes)
