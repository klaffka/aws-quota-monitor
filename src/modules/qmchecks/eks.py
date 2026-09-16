"""EKS quotas from cluster configuration and complete resource inventories."""
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def clusters(ctx):
    # The default listing excludes external Connector registrations.
    return ctx.call('eks', 'list_clusters', 'clusters')


def registered_clusters(ctx):
    count = 0
    for name in ctx.call('eks', 'list_clusters', 'clusters', include=['all']):
        cluster = ctx.call('eks', 'describe_cluster', name=name)['cluster']
        count += bool(cluster.get('connectorConfig'))
    return dict(usage=count, source='eks:ListClusters+DescribeCluster', method='ACCOUNT_COUNT')


def children_per_cluster(ctx, method, key):
    values = [(name, len(ctx.call('eks', method, key, clusterName=name)), None)
              for name in clusters(ctx)]
    return maximum(values, 'EKSCluster', f'eks:ListClusters+{method}')


def nodegroups_per_cluster(ctx):
    return children_per_cluster(ctx, 'list_nodegroups', 'nodegroups')


def fargate_profiles_per_cluster(ctx):
    return children_per_cluster(ctx, 'list_fargate_profiles', 'fargateProfileNames')


def cluster_configuration(ctx, section, field):
    values = []
    for name in clusters(ctx):
        cluster = ctx.call('eks', 'describe_cluster', name=name)['cluster']
        if section == 'remoteNetworkConfig':
            # Hybrid networking is optional. The array contains a wrapper;
            # quota usage is the CIDRs inside it, not the number of wrappers.
            networks = (cluster.get(section) or {}).get(field, [])
            usage = sum(len(network['cidrs']) for network in networks)
        else:
            config = cluster.get(section)
            if not isinstance(config, dict) or field not in config:
                raise NoData(f'EKS cluster configuration is missing {section}.{field}')
            usage = len(config[field])
        values.append((name, usage, None))
    return maximum(values, 'EKSCluster', 'eks:DescribeCluster')


def fargate_configuration(ctx, labels=False):
    values = []
    for cluster in clusters(ctx):
        for name in ctx.call('eks', 'list_fargate_profiles', 'fargateProfileNames', clusterName=cluster):
            profile = ctx.call('eks', 'describe_fargate_profile', clusterName=cluster,
                               fargateProfileName=name)['fargateProfile']
            selectors = profile.get('selectors')
            if not isinstance(selectors, list):
                raise NoData('EKS Fargate profile is missing selectors')
            identity = f'{cluster}/{name}'
            if labels:
                values.extend((f'{identity}/selector/{index}', len(selector.get('labels', {})), None)
                              for index, selector in enumerate(selectors))
            else:
                values.append((identity, len(selectors), None))
    return maximum(values, 'FargateSelector' if labels else 'FargateProfile', 'eks:DescribeFargateProfile')


def access_entries(ctx):
    values = []
    for name in clusters(ctx):
        cluster = ctx.call('eks', 'describe_cluster', name=name)['cluster']
        mode = (cluster.get('accessConfig') or {}).get('authenticationMode')
        if mode == 'CONFIG_MAP':
            count = 0
        elif mode in {'API', 'API_AND_CONFIG_MAP'}:
            count = len(ctx.call('eks', 'list_access_entries', 'accessEntries', clusterName=name))
        else:
            raise NoData('EKS cluster authentication mode is missing or unknown')
        values.append((name, count, None))
    return maximum(values, 'EKSCluster', 'eks:DescribeCluster+ListAccessEntries')


def managed_nodes(ctx):
    values = []
    for cluster in clusters(ctx):
        for name in ctx.call('eks', 'list_nodegroups', 'nodegroups', clusterName=cluster):
            nodegroup = ctx.call('eks', 'describe_nodegroup', clusterName=cluster, nodegroupName=name)['nodegroup']
            resources = nodegroup.get('resources') or {}
            groups = resources.get('autoScalingGroups')
            if not isinstance(groups, list) or not groups:
                raise NoData('EKS node group has no resolved Auto Scaling groups')
            instances = set()
            for group in groups:
                found = ctx.call('autoscaling', 'describe_auto_scaling_groups', 'AutoScalingGroups',
                                 AutoScalingGroupNames=[group['name']])
                if len(found) != 1 or found[0].get('AutoScalingGroupName') != group['name']:
                    raise NoData('EKS node group Auto Scaling inventory is incomplete')
                if 'Instances' not in found[0]:
                    raise NoData('EKS node group Auto Scaling inventory has no instance list')
                # Pending/terminating members still belong to the group. Do not
                # replace actual membership by maxSize or desiredSize targets.
                instances.update(instance['InstanceId'] for instance in found[0]['Instances'])
            values.append((f'{cluster}/{name}', len(instances), None))
    return maximum(values, 'EKSNodegroup', 'eks:DescribeNodegroup+autoscaling:DescribeAutoScalingGroups')


CHECKS = [
    ('L-1194D53C', 'Clusters', lambda c: dict(usage=len(clusters(c)), source='eks:ListClusters', method='ACCOUNT_COUNT')),
    ('L-6D54EA21', 'Managed node groups per cluster', nodegroups_per_cluster),
    ('L-33415657', 'Fargate profiles per cluster', fargate_profiles_per_cluster),
    ('L-FDFA5F81', 'Registered clusters', registered_clusters),
]

CONFIGURATION_CHECKS = [
    ('L-93A74D60', 'Public endpoint access CIDR ranges per cluster', partial(cluster_configuration, section='resourcesVpcConfig', field='publicAccessCidrs')),
    ('L-11427A54', 'Control plane security groups per cluster', partial(cluster_configuration, section='resourcesVpcConfig', field='securityGroupIds')),
    ('L-5C12D558', 'Remote node networks per cluster', partial(cluster_configuration, section='remoteNetworkConfig', field='remoteNodeNetworks')),
    ('L-6AFFD1D8', 'Remote pod networks per cluster', partial(cluster_configuration, section='remoteNetworkConfig', field='remotePodNetworks')),
    ('L-23414FF3', 'Label pairs per Fargate profile selector', partial(fargate_configuration, labels=True)),
    ('L-D78D8AF8', 'Selectors per Fargate profile', fargate_configuration),
    ('L-BD136A63', 'Nodes per managed node group', managed_nodes),
    ('L-C56B9FC3', 'Access entries per cluster', access_entries),
    ('L-EA277FDC', 'EKS Anywhere Enterprise Subscriptions', lambda c: dict(
        usage=len(c.call('eks', 'list_eks_anywhere_subscriptions', 'subscriptions',
                         includeStatus=['CREATING', 'ACTIVE', 'UPDATING', 'EXPIRING', 'EXPIRED', 'DELETING'])),
        source='eks:ListEksAnywhereSubscriptions', method='ACCOUNT_COUNT')),
]
ALL_CHECKS = CHECKS + CONFIGURATION_CHECKS


def get_current_quotastatus_eks(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'eks' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in CONFIGURATION_CHECKS if ('eks', check[0]) in context.quotas]
    return context.run('eks', checks, skip)
