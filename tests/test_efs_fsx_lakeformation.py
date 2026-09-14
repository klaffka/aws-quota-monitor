from unittest.mock import Mock

from modules.qmchecks.efs import access_points_per_file_system
from modules.qmchecks.fsx import CHECKS as FSX_CHECKS
from modules.qmchecks.lakeformation import administrators
from modules.qmchecks.neptune import endpoints_per_cluster


def test_efs_access_points_use_maximum_per_file_system():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'FileSystemId': 'fs-1'}, {'FileSystemId': 'fs-2'}],
        [{'AccessPointId': 'one'}],
        [{'AccessPointId': 'one'}, {'AccessPointId': 'two'}],
    ]
    result = access_points_per_file_system(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'fs-2')


def test_fsx_checks_filter_file_system_type_and_lustre_deployment():
    ctx = Mock()
    ctx.call.return_value = [
        {'FileSystemType': 'ONTAP'},
        {'FileSystemType': 'LUSTRE', 'LustreConfiguration': {'DeploymentType': 'PERSISTENT_1'}},
        {'FileSystemType': 'LUSTRE', 'LustreConfiguration': {'DeploymentType': 'SCRATCH_1'}},
    ]
    assert FSX_CHECKS[0][2](ctx)['usage'] == 1
    assert FSX_CHECKS[3][2](ctx)['usage'] == 1
    assert FSX_CHECKS[5][2](ctx)['usage'] == 1
    assert FSX_CHECKS[6][2](ctx)['usage'] == 0


def test_lakeformation_administrators_read_data_lake_settings():
    ctx = Mock()
    ctx.call.return_value = {'DataLakeSettings': {'DataLakeAdmins': [{'DataLakePrincipalIdentifier': 'a'}]}}
    assert administrators(ctx)['usage'] == 1


def test_neptune_cluster_endpoints_use_maximum_per_cluster():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'DBClusterIdentifier': 'cluster-a'}, {'DBClusterIdentifier': 'cluster-b'}],
        [{'Endpoint': 'a'}],
        [{'Endpoint': 'a'}, {'Endpoint': 'b'}],
    ]
    result = endpoints_per_cluster(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'cluster-b')


def test_neptune_parameter_group_checks_count_paginated_inventories():
    from modules.qmchecks.neptune import CHECKS
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'one'}, {'Name': 'two'}]
    assert [check(ctx)['usage'] for code, _, check in CHECKS if code in {'L-584DADE7', 'L-5BB9A916'}] == [2, 2]


def test_neptune_read_replicas_use_explicit_instance_role():
    from modules.qmchecks.neptune import read_replicas_per_cluster
    ctx = Mock()
    ctx.call.return_value = [
        {'DBClusterIdentifier': 'cluster', 'DBInstanceRole': 'WRITER'},
        {'DBClusterIdentifier': 'cluster', 'DBInstanceRole': 'READ_REPLICA'},
        {'DBClusterIdentifier': 'cluster', 'DBInstanceRole': 'READ_REPLICA'},
    ]
    assert read_replicas_per_cluster(ctx)['usage'] == 2
