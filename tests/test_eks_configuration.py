from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.eks import (
    CHECKS, CONFIGURATION_CHECKS, access_entries, cluster_configuration,
    fargate_configuration, get_current_quotastatus_eks, managed_nodes,
)
from modules.qmcore.aws import CheckContext, NoData
from datetime import UTC


def context(quotas=()):
    return CheckContext(boto3.Session(region_name='eu-central-1'), quotas, account='123456789012')


def test_cluster_configuration_counts_cidrs_inside_wrapper_and_customer_security_groups():
    ctx = context()
    with Stubber(ctx.client('eks')) as stub:
        stub.add_response('list_clusters', {'clusters': ['first'], 'nextToken': 'next'}, {})
        stub.add_response('list_clusters', {'clusters': ['second']}, {'nextToken': 'next'})
        stub.add_response('describe_cluster', {'cluster': {
            'resourcesVpcConfig': {'securityGroupIds': ['sg-one'], 'clusterSecurityGroupId': 'sg-managed',
                                   'endpointPublicAccess': False, 'publicAccessCidrs': ['0.0.0.0/0', '::/0']},
            'remoteNetworkConfig': {'remoteNodeNetworks': [{'cidrs': ['10.0.0.0/16', '10.1.0.0/16', '10.2.0.0/16']}],
                                    'remotePodNetworks': [{'cidrs': ['172.16.0.0/16']}]}}}, {'name': 'first'})
        stub.add_response('describe_cluster', {'cluster': {
            'resourcesVpcConfig': {'securityGroupIds': [], 'publicAccessCidrs': ['0.0.0.0/0']}}}, {'name': 'second'})
        assert cluster_configuration(ctx, 'remoteNetworkConfig', 'remoteNodeNetworks')['usage'] == 3
        assert cluster_configuration(ctx, 'remoteNetworkConfig', 'remotePodNetworks')['usage'] == 1
        assert cluster_configuration(ctx, 'resourcesVpcConfig', 'securityGroupIds')['usage'] == 1
        assert cluster_configuration(ctx, 'resourcesVpcConfig', 'publicAccessCidrs')['usage'] == 2
        stub.assert_no_pending_responses()


def test_missing_required_vpc_data_does_not_become_zero():
    ctx = Mock()
    ctx.call.side_effect = [['cluster'], {'cluster': {}}]
    with pytest.raises(NoData):
        cluster_configuration(ctx, 'resourcesVpcConfig', 'securityGroupIds')


def test_fargate_selectors_and_labels_use_their_own_parent_maximum():
    ctx = context()
    with Stubber(ctx.client('eks')) as stub:
        stub.add_response('list_clusters', {'clusters': ['cluster']}, {})
        stub.add_response('list_fargate_profiles', {'fargateProfileNames': ['one', 'two']}, {'clusterName': 'cluster'})
        stub.add_response('describe_fargate_profile', {'fargateProfile': {'selectors': [
            {'namespace': '*', 'labels': {'app': '*', 'env': 'prod'}}, {'namespace': 'default'}]}},
                          {'clusterName': 'cluster', 'fargateProfileName': 'one'})
        stub.add_response('describe_fargate_profile', {'fargateProfile': {'selectors': [
            {'namespace': 'other', 'labels': {'a': '1', 'b': '2', 'c': '3'}}]}},
                          {'clusterName': 'cluster', 'fargateProfileName': 'two'})
        assert fargate_configuration(ctx)['usage'] == 2
        labels = fargate_configuration(ctx, labels=True)
        assert labels['usage'] == 3
        assert labels['resource_id'] == 'cluster/two/selector/0'


def test_managed_nodes_use_asg_membership_across_all_backing_groups():
    ctx = context()
    with Stubber(ctx.client('eks')) as eks, Stubber(ctx.client('autoscaling')) as asg:
        eks.add_response('list_clusters', {'clusters': ['cluster']}, {})
        eks.add_response('list_nodegroups', {'nodegroups': ['nodegroup']}, {'clusterName': 'cluster'})
        eks.add_response('describe_nodegroup', {'nodegroup': {
            'scalingConfig': {'minSize': 0, 'desiredSize': 50, 'maxSize': 100},
            'resources': {'autoScalingGroups': [{'name': 'first'}, {'name': 'second'}]}}},
                         {'clusterName': 'cluster', 'nodegroupName': 'nodegroup'})
        from datetime import datetime
        for name, members in [('first', [('i-one', 'InService'), ('i-two', 'Pending')]),
                              ('second', [('i-three', 'Terminating')])]:
            group = dict(AutoScalingGroupName=name, MinSize=0, MaxSize=100, DesiredCapacity=50,
                         DefaultCooldown=300, AvailabilityZones=['eu-central-1a'],
                         HealthCheckType='EC2', CreatedTime=datetime.now(UTC),
                         Instances=[{'InstanceId': identity, 'AvailabilityZone': 'eu-central-1a',
                                     'LifecycleState': state, 'HealthStatus': 'Healthy',
                                     'ProtectedFromScaleIn': False} for identity, state in members])
            asg.add_response('describe_auto_scaling_groups', {'AutoScalingGroups': [group]}, {'AutoScalingGroupNames': [name]})
        result = managed_nodes(ctx)
        assert result['usage'] == 3
        assert result['resource_id'] == 'cluster/nodegroup'


def test_missing_asg_prevents_partial_node_count():
    ctx = Mock()
    ctx.call.side_effect = [['cluster'], ['group'], {'nodegroup': {'resources': {
        'autoScalingGroups': [{'name': 'one'}, {'name': 'two'}]}}},
        [{'AutoScalingGroupName': 'one', 'Instances': [{'InstanceId': 'i-one'}]}], []]
    with pytest.raises(NoData, match='incomplete'):
        managed_nodes(ctx)


def test_access_entries_skip_configmap_only_clusters():
    ctx = context()
    with Stubber(ctx.client('eks')) as stub:
        stub.add_response('list_clusters', {'clusters': ['legacy', 'api']}, {})
        stub.add_response('describe_cluster', {'cluster': {'accessConfig': {'authenticationMode': 'CONFIG_MAP'}}}, {'name': 'legacy'})
        stub.add_response('describe_cluster', {'cluster': {'accessConfig': {'authenticationMode': 'API_AND_CONFIG_MAP'}}}, {'name': 'api'})
        stub.add_response('list_access_entries', {'accessEntries': ['arn:aws:iam::123456789012:role/one'], 'nextToken': 'next'}, {'clusterName': 'api'})
        stub.add_response('list_access_entries', {'accessEntries': ['arn:aws:iam::123456789012:role/two']}, {'clusterName': 'api', 'nextToken': 'next'})
        assert access_entries(ctx)['usage'] == 2


def test_subscription_inventory_requests_each_resource_state_on_its_own():
    """EKS rejects a repeated includeStatus key, so one state goes per call."""
    ctx = context([{'ServiceCode': 'eks', 'QuotaCode': 'L-EA277FDC', 'Value': 10}])
    listed = {'ACTIVE': [{'id': 'one', 'status': 'ACTIVE'}, {'id': 'moving', 'status': 'ACTIVE'}],
              # Changed state between two calls: still one subscription.
              'EXPIRING': [{'id': 'moving', 'status': 'EXPIRING'}],
              'EXPIRED': [{'id': 'two', 'status': 'EXPIRED'}]}
    with Stubber(ctx.client('eks')) as stub:
        for state in ('CREATING', 'ACTIVE', 'UPDATING', 'EXPIRING', 'EXPIRED', 'DELETING'):
            stub.add_response('list_eks_anywhere_subscriptions',
                              {'subscriptions': listed.get(state, [])}, {'includeStatus': [state]})
        row, = get_current_quotastatus_eks(ctx=ctx, skip={('eks', code) for code, _, _ in CHECKS})
        stub.assert_no_pending_responses()
    assert row['qualityStatus'] == 'OK'
    assert row['usageValue'] == 3


def test_optional_config_checks_are_only_selected_for_present_catalog_quotas():
    ctx = Mock(quotas={('eks', 'L-1194D53C'): {}})
    ctx.run.return_value = []
    get_current_quotastatus_eks(ctx=ctx)
    assert ctx.run.call_args.args[1] == CHECKS
    assert len(CONFIGURATION_CHECKS) == 9
