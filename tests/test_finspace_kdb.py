from unittest.mock import Mock

import pytest

from modules.qmchecks import finspace
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants


class FinSpaceContext:
    def __init__(self):
        self.environment_data = {
            'env-a': {
                'clusters': [
                    {'clusterName': 'dedicated-a', 'azMode': 'SINGLE'},
                    {'clusterName': 'scaling-a', 'azMode': 'MULTI'},
                ],
                'details': {
                    'dedicated-a': {
                        'clusterName': 'dedicated-a',
                        'capacityConfiguration': {'nodeType': 'kx.s.large'},
                        'savedownStorageConfiguration': {'size': 20},
                        'cacheStorageConfigurations': [{'size': 10}],
                    },
                    'scaling-a': {
                        'clusterName': 'scaling-a',
                        'scalingGroupConfiguration': {'scalingGroupName': 'group-a'},
                        'cacheStorageConfigurations': [],
                    },
                },
                'nodes': {'dedicated-a': ['a-1'], 'scaling-a': ['a-2', 'a-3']},
                'groups': [{'scalingGroupName': 'group-a', 'hostType': 'kx.sg.large'}],
                'users': ['alice'],
                'volumes': {'volume-a': 100},
                'databases': {'database-a': ['view-a']},
            },
            'env-b': {
                'clusters': [
                    {'clusterName': 'dedicated-b', 'azMode': 'SINGLE'},
                    {'clusterName': 'scaling-b', 'azMode': 'MULTI'},
                    {'clusterName': 'scaling-c', 'azMode': 'MULTI'},
                ],
                'details': {
                    'dedicated-b': {
                        'clusterName': 'dedicated-b',
                        'capacityConfiguration': {'nodeType': 'kx.s.large'},
                        'savedownStorageConfiguration': {'size': 30},
                        'cacheStorageConfigurations': [{'size': 12}, {'size': 13}],
                    },
                    'scaling-b': {
                        'clusterName': 'scaling-b',
                        'scalingGroupConfiguration': {'scalingGroupName': 'group-b'},
                    },
                    'scaling-c': {
                        'clusterName': 'scaling-c',
                        'scalingGroupConfiguration': {'scalingGroupName': 'group-b'},
                        'savedownStorageConfiguration': {'size': 10},
                    },
                },
                'nodes': {
                    'dedicated-b': ['b-1', 'b-2', 'b-3'],
                    'scaling-b': ['b-4', 'b-5'],
                    'scaling-c': ['b-6', 'b-7', 'b-8'],
                },
                'groups': [{'scalingGroupName': 'group-b', 'hostType': 'kx.sg.2xlarge'}],
                'users': ['bob', 'carol', 'dave'],
                'volumes': {'volume-b': 200, 'volume-c': 250},
                'databases': {'database-b': ['view-b', 'view-c'], 'database-c': ['view-d']},
            },
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'finspace'
        if method == 'list_kx_environments':
            return [{'environmentId': environment_id}
                    for environment_id in reversed(self.environment_data)]
        environment_id = kwargs['environmentId']
        data = self.environment_data[environment_id]
        if method == 'list_kx_clusters':
            return data['clusters']
        if method == 'get_kx_cluster':
            return data['details'][kwargs['clusterName']]
        if method == 'list_kx_cluster_nodes':
            return [{'nodeId': node} for node in data['nodes'][kwargs['clusterName']]]
        if method == 'list_kx_scaling_groups':
            return data['groups']
        if method == 'list_kx_users':
            return [{'userName': user} for user in data['users']]
        if method == 'list_kx_volumes':
            return [{'volumeName': volume} for volume in data['volumes']]
        if method == 'get_kx_volume':
            volume = kwargs['volumeName']
            return {'environmentId': environment_id, 'volumeName': volume,
                    'nas1Configuration': {'size': data['volumes'][volume]}}
        if method == 'list_kx_databases':
            return [{'databaseName': database} for database in data['databases']]
        if method == 'list_kx_dataviews':
            return [{'dataviewName': view}
                    for view in data['databases'][kwargs['databaseName']]]
        raise AssertionError(method)


def test_finspace_resource_checks_use_maximum_per_environment():
    ctx = FinSpaceContext()

    assert (finspace.cluster_count(ctx)['usage'],
            finspace.cluster_count(ctx)['resource_id']) == (3, 'env-b')
    assert finspace.cluster_count(ctx, 'SINGLE')['usage'] == 1
    assert finspace.cluster_count(ctx, 'MULTI')['usage'] == 2
    assert finspace.environment_count(ctx, 'list_kx_users', 'users',
                                      'userName', 'user')['usage'] == 3
    assert finspace.environment_count(ctx, 'list_kx_scaling_groups', 'scalingGroups',
                                      'scalingGroupName', 'scaling group')['usage'] == 1
    assert finspace.environment_count(ctx, 'list_kx_volumes', 'kxVolumeSummaries',
                                      'volumeName', 'volume')['usage'] == 2
    assert finspace.database_count(ctx)['usage'] == 2
    assert finspace.dataview_count(ctx)['usage'] == 3


def test_finspace_node_checks_count_live_nodes_by_compute_type():
    ctx = FinSpaceContext()

    dedicated = finspace.node_count(ctx, 'kx.s.large')
    scaling = finspace.node_count(ctx, 'kx.sg.2xlarge', scaling_group=True)
    unused = finspace.node_count(ctx, 'kx.s.32xlarge')

    assert (dedicated['usage'], dedicated['resource_id']) == (3, 'env-b')
    assert (scaling['usage'], scaling['resource_id']) == (5, 'env-b')
    assert unused['usage'] == 0


def test_finspace_storage_checks_sum_each_environment_independently():
    ctx = FinSpaceContext()

    assert finspace.volume_storage(ctx)['usage'] == 450
    assert finspace.cluster_storage(ctx, 'savedownStorageConfiguration')['usage'] == 40
    assert finspace.cluster_storage(ctx, 'cacheStorageConfigurations', nested=True)['usage'] == 25


def test_finspace_inconsistent_inventory_is_no_data():
    ctx = FinSpaceContext()
    ctx.environment_data['env-a']['groups'] = []
    with pytest.raises(NoData, match='unknown scaling group'):
        finspace.node_count(ctx, 'kx.sg.large', scaling_group=True)

    ctx = FinSpaceContext()
    ctx.environment_data['env-b']['volumes']['volume-b'] = -1
    with pytest.raises(NoData, match='valid size'):
        finspace.volume_storage(ctx)


def test_finspace_extended_checks_are_catalog_backed_and_selected_by_quota():
    assert len(finspace.ALL_CHECKS) == 28
    assert {('finspace', code) for code, _name, _check in finspace.ALL_CHECKS} <= custom_keys()

    context = Mock(quotas={('finspace', 'L-403A8F92'): {}})
    context.run.return_value = []
    assert finspace.get_current_quotastatus_finspace(ctx=context) == []
    selected = context.run.call_args.args[1]
    assert [code for code, _name, _check in selected] == ['L-C49840B4', 'L-403A8F92']


def test_finspace_checks_have_required_read_permissions():
    for action in (
        'ListKxEnvironments', 'ListKxClusters', 'GetKxCluster', 'ListKxClusterNodes',
        'ListKxScalingGroups', 'ListKxUsers', 'ListKxVolumes', 'GetKxVolume',
        'ListKxDatabases', 'ListKxDataviews',
    ):
        assert grants(f'finspace:{action}')
