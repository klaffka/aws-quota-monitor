"""AWS FinSpace Managed kdb resource usage from complete regional inventories."""
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def unique(items, field, subject):
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'FinSpace {subject} inventory contains an invalid item')
        identity = item.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'FinSpace {subject} is missing {field}')
        if identity in result and result[identity] != item:
            raise NoData(f'FinSpace {subject} inventory changed during pagination')
        result[identity] = item
    return [result[key] for key in sorted(result)]


def environments(ctx):
    return unique(ctx.call('finspace', 'list_kx_environments', 'environments'),
                  'environmentId', 'environment')


def environment_items(ctx, environment, method, key, identity, subject, **kwargs):
    environment_id = environment['environmentId']
    return unique(ctx.call('finspace', method, key, environmentId=environment_id, **kwargs),
                  identity, subject)


def per_environment(ctx, measure, source):
    values = []
    for environment in environments(ctx):
        environment_id = environment['environmentId']
        values.append((environment_id, measure(environment), None))
    return maximum(values, 'FinSpaceKxEnvironment', source)


def clusters(ctx, environment):
    return environment_items(ctx, environment, 'list_kx_clusters', 'kxClusterSummaries',
                             'clusterName', 'cluster')


def cluster_count(ctx, az_mode=None):
    def measure(environment):
        items = clusters(ctx, environment)
        if az_mode is None:
            return len(items)
        for item in items:
            if item.get('azMode') not in {'SINGLE', 'MULTI'}:
                raise NoData('FinSpace cluster is missing a valid azMode')
        return sum(item['azMode'] == az_mode for item in items)

    return per_environment(ctx, measure, 'finspace:ListKxClusters')


def cluster_details(ctx, environment, include_nodes=False):
    environment_id = environment['environmentId']
    result = []
    for summary in clusters(ctx, environment):
        name = summary['clusterName']
        detail = ctx.call('finspace', 'get_kx_cluster', environmentId=environment_id,
                          clusterName=name)
        if not isinstance(detail, dict) or detail.get('clusterName') != name:
            raise NoData('FinSpace cluster detail is inconsistent')
        nodes = []
        if include_nodes:
            nodes = unique(ctx.call('finspace', 'list_kx_cluster_nodes', 'nodes',
                                    environmentId=environment_id, clusterName=name),
                           'nodeId', 'cluster node')
        result.append((detail, nodes))
    return result


def node_count(ctx, node_type, scaling_group=False):
    def measure(environment):
        host_types = {}
        if scaling_group:
            groups = environment_items(ctx, environment, 'list_kx_scaling_groups',
                                       'scalingGroups', 'scalingGroupName', 'scaling group')
            host_types = {group['scalingGroupName']: group.get('hostType') for group in groups}
            if any(not isinstance(value, str) or not value for value in host_types.values()):
                raise NoData('FinSpace scaling group is missing hostType')
        total = 0
        for detail, nodes in cluster_details(ctx, environment, include_nodes=True):
            if scaling_group:
                configuration = detail.get('scalingGroupConfiguration')
                if not configuration:
                    continue
                group_name = configuration.get('scalingGroupName')
                if group_name not in host_types:
                    raise NoData('FinSpace cluster references an unknown scaling group')
                current_type = host_types[group_name]
            else:
                configuration = detail.get('capacityConfiguration')
                if not configuration:
                    continue
                current_type = configuration.get('nodeType')
                if not isinstance(current_type, str) or not current_type:
                    raise NoData('FinSpace dedicated cluster is missing nodeType')
            if current_type == node_type:
                total += len(nodes)
        return total

    source = ('finspace:ListKxClusters+GetKxCluster+ListKxClusterNodes'
              + ('+ListKxScalingGroups' if scaling_group else ''))
    return per_environment(ctx, measure, source)


def environment_count(ctx, method, key, identity, subject):
    def measure(environment):
        return len(environment_items(ctx, environment, method, key, identity, subject))

    return per_environment(ctx, measure, f'finspace:{method}')


def database_count(ctx):
    return environment_count(ctx, 'list_kx_databases', 'kxDatabases',
                             'databaseName', 'database')


def dataview_count(ctx):
    def measure(environment):
        total = 0
        databases = environment_items(ctx, environment, 'list_kx_databases', 'kxDatabases',
                                      'databaseName', 'database')
        for database in databases:
            views = environment_items(ctx, environment, 'list_kx_dataviews', 'kxDataviews',
                                      'dataviewName', 'dataview',
                                      databaseName=database['databaseName'])
            total += len(views)
        return total

    return per_environment(ctx, measure, 'finspace:ListKxDatabases+ListKxDataviews')


def nonnegative_integer(value, subject):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise NoData(f'FinSpace {subject} is missing a valid size')
    return value


def cluster_storage(ctx, field, nested=False):
    def measure(environment):
        total = 0
        for detail, _nodes in cluster_details(ctx, environment):
            value = detail.get(field)
            configurations = (value or []) if nested else ([] if value is None else [value])
            if not isinstance(configurations, list):
                raise NoData(f'FinSpace cluster has an invalid {field}')
            for configuration in configurations:
                if not isinstance(configuration, dict):
                    raise NoData(f'FinSpace cluster has an invalid {field}')
                total += nonnegative_integer(configuration.get('size'), field)
        return total

    return per_environment(ctx, measure, 'finspace:ListKxClusters+GetKxCluster')


def volume_storage(ctx):
    def measure(environment):
        environment_id = environment['environmentId']
        total = 0
        volumes = environment_items(ctx, environment, 'list_kx_volumes', 'kxVolumeSummaries',
                                   'volumeName', 'volume')
        for volume in volumes:
            name = volume['volumeName']
            detail = ctx.call('finspace', 'get_kx_volume', environmentId=environment_id,
                              volumeName=name)
            if not isinstance(detail, dict) or detail.get('environmentId') != environment_id \
                    or detail.get('volumeName') != name:
                raise NoData('FinSpace volume detail is inconsistent')
            configuration = detail.get('nas1Configuration')
            if not isinstance(configuration, dict):
                raise NoData('FinSpace volume is missing NAS-1 configuration')
            total += nonnegative_integer(configuration.get('size'), 'volume storage')
        return total

    return per_environment(ctx, measure, 'finspace:ListKxVolumes+GetKxVolume')


CHECKS = [('L-C49840B4', 'Total kdb environments',
           lambda ctx: dict(usage=len(environments(ctx)),
                            source='finspace:ListKxEnvironments', method='ACCOUNT_COUNT'))]

EXTENDED_CHECKS = [
    ('L-403A8F92', 'Managed kdb clusters', cluster_count),
    ('L-7CF802FB', 'Managed kdb multi-AZ clusters', partial(cluster_count, az_mode='MULTI')),
    ('L-7E609E02', 'Managed kdb single-AZ clusters', partial(cluster_count, az_mode='SINGLE')),
    ('L-A18C5C9A', 'Managed kdb cluster users',
     partial(environment_count, method='list_kx_users', key='users',
             identity='userName', subject='user')),
    ('L-8F9600BF', 'Managed kdb scaling groups',
     partial(environment_count, method='list_kx_scaling_groups', key='scalingGroups',
             identity='scalingGroupName', subject='scaling group')),
    ('L-9DDBB72F', 'Managed kdb volumes',
     partial(environment_count, method='list_kx_volumes', key='kxVolumeSummaries',
             identity='volumeName', subject='volume')),
    ('L-2B5C0922', 'Managed kdb volume storage', volume_storage),
    ('L-9EDD8654', 'Managed kdb savedown storage',
     partial(cluster_storage, field='savedownStorageConfiguration')),
    ('L-C8CECF7C', 'Managed kdb database cluster cache size',
     partial(cluster_storage, field='cacheStorageConfigurations', nested=True)),
    ('L-EB49E8B0', 'Managed kdb databases', database_count),
    ('L-4F92BAA2', 'Managed kdb dataviews', dataview_count),
]

DEDICATED_NODE_QUOTAS = {
    'L-816D4CEA': 'kx.s.large',
    'L-8D2987C0': 'kx.s.xlarge',
    'L-3B1B408E': 'kx.s.2xlarge',
    'L-6271C28F': 'kx.s.4xlarge',
    'L-79C359E7': 'kx.s.8xlarge',
    'L-8995E194': 'kx.s.16xlarge',
    'L-BA1748AE': 'kx.s.32xlarge',
}
SCALING_NODE_QUOTAS = {
    'L-1F5558B4': 'kx.sg.large',
    'L-256AB33A': 'kx.sg.xlarge',
    'L-186ACF90': 'kx.sg.2xlarge',
    'L-9EFEF0D8': 'kx.sg.4xlarge',
    'L-8116797B': 'kx.sg.8xlarge',
    'L-B75F5AE2': 'kx.sg.16xlarge',
    'L-F9DDF688': 'kx.sg.32xlarge',
    'L-EE85DFB8': 'kx.sg1.16xlarge',
    'L-8C2FDE0C': 'kx.sg1.24xlarge',
}
EXTENDED_CHECKS += [(code, f'{node_type} nodes', partial(node_count, node_type=node_type))
                    for code, node_type in DEDICATED_NODE_QUOTAS.items()]
EXTENDED_CHECKS += [(code, f'{node_type} scaling group nodes',
                     partial(node_count, node_type=node_type, scaling_group=True))
                    for code, node_type in SCALING_NODE_QUOTAS.items()]
ALL_CHECKS = CHECKS + EXTENDED_CHECKS


def get_current_quotastatus_finspace(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'finspace' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in EXTENDED_CHECKS
                       if ('finspace', check[0]) in context.quotas]
    return context.run('finspace', checks, skip)
