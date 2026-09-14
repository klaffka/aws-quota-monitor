"""Resource-count quotas for newer AWS control-plane services."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


LATTICE = 'vpc-lattice'
RESOURCE_STATES = {
    'ACTIVE', 'CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'DELETE_IN_PROGRESS',
    'CREATE_FAILED', 'UPDATE_FAILED', 'DELETE_FAILED',
}
COUNTED_RESOURCE_STATES = RESOURCE_STATES - {'CREATE_FAILED'}
ASSOCIATION_STATES = {
    'CREATE_IN_PROGRESS', 'ACTIVE', 'PARTIAL', 'UPDATE_IN_PROGRESS',
    'DELETE_IN_PROGRESS', 'CREATE_FAILED', 'UPDATE_FAILED', 'DELETE_FAILED',
}
COUNTED_ASSOCIATION_STATES = ASSOCIATION_STATES - {'CREATE_FAILED'}
TARGET_STATES = {'DRAINING', 'UNAVAILABLE', 'HEALTHY', 'UNHEALTHY', 'INITIAL', 'UNUSED'}
DOMAIN_STATES = {'VERIFIED', 'PENDING', 'VERIFICATION_TIMED_OUT'}
RESOURCE_CONFIGURATION_TYPES = {'GROUP', 'CHILD', 'SINGLE', 'ARN'}


def count(api, method, key):
    return lambda c: dict(usage=len(c.call(api, method, key)),
                          source=f'{api}:{method}', method='ACCOUNT_COUNT')


def _validate_arn(arn, ctx, prefix, subject, *, owned=None):
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != LATTICE
            or parts[3] != ctx.region or not parts[4].isdigit()
            or len(parts[4]) != 12 or not parts[5].startswith(prefix)
            or len(parts[5]) <= len(prefix)):
        raise NoData(f'VPC Lattice {subject} has an inconsistent ARN')
    if owned is True and parts[4] != ctx.account:
        return False
    if owned is False and parts[4] == ctx.account:
        return False
    return True


def _inventory(ctx, method, prefix, subject, *, states=None, counted=None,
               owned=False, **kwargs):
    result = {}
    for item in ctx.call(LATTICE, method, 'items', **kwargs):
        if not isinstance(item, dict):
            raise NoData(f'VPC Lattice {subject} inventory contains an invalid item')
        raw_identifier = item.get('id')
        arn = item.get('arn')
        if not isinstance(raw_identifier, str) or not raw_identifier:
            raise NoData(f'VPC Lattice {subject} is missing its ID')
        identifier = raw_identifier.rsplit('/', 1)[-1]
        is_owned = _validate_arn(arn, ctx, prefix, subject, owned=True)
        if raw_identifier.startswith('arn:') and raw_identifier != arn:
            raise NoData(f'VPC Lattice {subject} ID and ARN are inconsistent')
        if not arn.endswith(f'/{identifier}'):
            raise NoData(f'VPC Lattice {subject} ID and ARN are inconsistent')
        if states is not None and item.get('status') not in states:
            raise NoData(f'VPC Lattice {subject} has an unknown state')
        if owned and not is_owned:
            continue
        if identifier in result:
            if result[identifier] != item:
                raise NoData(f'VPC Lattice {subject} changed during pagination')
            continue
        result[identifier] = item
    if counted is not None:
        result = {key: item for key, item in result.items()
                  if item['status'] in counted}
    return result


def service_networks(ctx):
    return _inventory(ctx, 'list_service_networks', 'servicenetwork/',
                      'service network', owned=True)


def services(ctx):
    return _inventory(ctx, 'list_services', 'service/', 'service',
                      states=RESOURCE_STATES, counted=COUNTED_RESOURCE_STATES,
                      owned=True)


def target_groups(ctx):
    items = _inventory(ctx, 'list_target_groups', 'targetgroup/', 'target group',
                       states=RESOURCE_STATES, counted=COUNTED_RESOURCE_STATES,
                       owned=True)
    for item in items.values():
        arns = item.get('serviceArns', [])
        if not isinstance(arns, list) or any(not isinstance(arn, str) or not arn
                                             for arn in arns):
            raise NoData('VPC Lattice target group has no complete service inventory')
        if len(arns) != len(set(arns)):
            raise NoData('VPC Lattice target group has duplicate service associations')
    return items


def resource_configurations(ctx, **kwargs):
    items = _inventory(
        ctx, 'list_resource_configurations', 'resourceconfiguration/',
        'resource configuration', states=RESOURCE_STATES,
        counted=COUNTED_RESOURCE_STATES, owned=True, **kwargs)
    for item in items.values():
        kind = item.get('type')
        parent = item.get('resourceConfigurationGroupId')
        if kind not in RESOURCE_CONFIGURATION_TYPES:
            raise NoData('VPC Lattice resource configuration has an unknown type')
        if kind == 'CHILD' and (not isinstance(parent, str) or not parent):
            raise NoData('VPC Lattice child resource configuration is missing its group')
        if kind != 'CHILD' and parent is not None:
            raise NoData('VPC Lattice resource configuration has an unexpected group')
    return items


def resource_gateways(ctx):
    items = _inventory(ctx, 'list_resource_gateways', 'resourcegateway/',
                       'resource gateway', states=RESOURCE_STATES,
                       counted=COUNTED_RESOURCE_STATES, owned=True)
    for item in items.values():
        vpc = item.get('vpcIdentifier')
        groups = item.get('securityGroupIds', [])
        if not isinstance(vpc, str) or not vpc.startswith('vpc-'):
            raise NoData('VPC Lattice resource gateway is missing its VPC')
        if (not isinstance(groups, list)
                or any(not isinstance(group, str) or not group.startswith('sg-')
                       for group in groups)
                or len(groups) != len(set(groups))):
            raise NoData('VPC Lattice resource gateway has an invalid security-group inventory')
    return items


def domain_verifications(ctx):
    return _inventory(ctx, 'list_domain_verifications', 'domainverification/',
                      'domain verification', states=DOMAIN_STATES, owned=True)


def account_count(items, source):
    return dict(usage=len(items), source=source, method='ACCOUNT_COUNT')


def lattice_listeners_per_service(ctx):
    values = []
    for service_id, service in services(ctx).items():
        items = _inventory(ctx, 'list_listeners',
                           f'service/{service_id}/listener/', 'listener',
                           owned=True, serviceIdentifier=service_id)
        values.append((service['arn'], len(items), None))
    return maximum(values, 'VpcLatticeService',
                   'vpc-lattice:ListServices+ListListeners')


def lattice_rules_per_listener(ctx):
    values = []
    for service_id in services(ctx):
        listeners = _inventory(ctx, 'list_listeners',
                               f'service/{service_id}/listener/', 'listener',
                               owned=True, serviceIdentifier=service_id)
        for listener_id, listener in listeners.items():
            rules = _inventory(
                ctx, 'list_rules',
                f'service/{service_id}/listener/{listener_id}/rule/', 'rule',
                owned=True, serviceIdentifier=service_id,
                listenerIdentifier=listener_id)
            values.append((listener['arn'], len(rules), None))
    return maximum(values, 'VpcLatticeListener',
                   'vpc-lattice:ListServices+ListListeners+ListRules')


def lattice_target_groups_per_service(ctx):
    known = services(ctx)
    by_arn = {item['arn']: item for item in known.values()}
    counts = Counter()
    for target_group in target_groups(ctx).values():
        for service_arn in target_group.get('serviceArns', []):
            if service_arn not in by_arn:
                raise NoData('VPC Lattice target group references an unknown owned service')
            counts[service_arn] += 1
    return maximum(((service['arn'], counts[service['arn']], None)
                    for service in known.values()),
                   'VpcLatticeService',
                   'vpc-lattice:ListServices+ListTargetGroups')


def lattice_targets_per_target_group(ctx):
    values = []
    for group_id, group in target_groups(ctx).items():
        found = {}
        for item in ctx.call(LATTICE, 'list_targets', 'items',
                             targetGroupIdentifier=group_id):
            if not isinstance(item, dict):
                raise NoData('VPC Lattice target inventory contains an invalid item')
            identifier = item.get('id')
            port = item.get('port')
            state = item.get('status')
            if (not isinstance(identifier, str) or not identifier
                    or (port is not None and (not isinstance(port, int)
                                              or isinstance(port, bool)
                                              or not 1 <= port <= 65535))):
                raise NoData('VPC Lattice target has an invalid identity')
            if state not in TARGET_STATES:
                raise NoData('VPC Lattice target has an unknown state')
            identity = (identifier, port)
            if identity in found:
                if found[identity] != item:
                    raise NoData('VPC Lattice target changed during pagination')
                continue
            found[identity] = item
        values.append((group['arn'], len(found), None))
    return maximum(values, 'VpcLatticeTargetGroup',
                   'vpc-lattice:ListTargetGroups+ListTargets')


def lattice_resource_gateways_per_vpc(ctx):
    counts = Counter(item['vpcIdentifier'] for item in resource_gateways(ctx).values())
    return maximum(((vpc, count, None) for vpc, count in counts.items()),
                   'Vpc', 'vpc-lattice:ListResourceGateways')


def lattice_children_per_group(ctx):
    parents = {key: item for key, item in resource_configurations(ctx).items()
               if item['type'] == 'GROUP'}
    values = []
    for group_id, group in parents.items():
        children = resource_configurations(
            ctx, resourceConfigurationGroupIdentifier=group_id)
        if any(item['type'] != 'CHILD'
               or item['resourceConfigurationGroupId'] != group_id
               for item in children.values()):
            raise NoData('VPC Lattice resource configuration has an inconsistent group')
        values.append((group['arn'], len(children), None))
    return maximum(values, 'VpcLatticeResourceConfigurationGroup',
                   'vpc-lattice:ListResourceConfigurations')


def _association_inventory(ctx, network, method, prefix, subject, states):
    items = _inventory(ctx, method, prefix, subject, states=states,
                       counted=COUNTED_ASSOCIATION_STATES,
                       serviceNetworkIdentifier=network['id'])
    for item in items.values():
        if (item.get('serviceNetworkId') != network['id']
                or item.get('serviceNetworkArn') != network['arn']):
            raise NoData(f'VPC Lattice {subject} has an inconsistent parent')
    return items


def lattice_service_associations_per_network(ctx):
    values = []
    for network in service_networks(ctx).values():
        items = _association_inventory(
            ctx, network, 'list_service_network_service_associations',
            'servicenetworkserviceassociation/', 'service association',
            ASSOCIATION_STATES - {'PARTIAL', 'UPDATE_IN_PROGRESS', 'UPDATE_FAILED'})
        values.append((network['arn'], len(items), None))
    return maximum(values, 'VpcLatticeServiceNetwork',
                   'vpc-lattice:ListServiceNetworks+ListServiceNetworkServiceAssociations')


def lattice_vpc_associations(ctx):
    result = {}
    for network in service_networks(ctx).values():
        items = _association_inventory(
            ctx, network, 'list_service_network_vpc_associations',
            'servicenetworkvpcassociation/', 'VPC association',
            ASSOCIATION_STATES - {'PARTIAL'})
        for key, item in items.items():
            if key in result:
                raise NoData('VPC Lattice VPC association appears under multiple networks')
            result[key] = item
    return result


def lattice_vpc_associations_per_network(ctx):
    counts = Counter(item['serviceNetworkArn']
                     for item in lattice_vpc_associations(ctx).values())
    networks = service_networks(ctx)
    return maximum(((network['arn'], counts[network['arn']], None)
                    for network in networks.values()),
                   'VpcLatticeServiceNetwork',
                   'vpc-lattice:ListServiceNetworks+ListServiceNetworkVpcAssociations')


def lattice_security_groups_per_association(ctx):
    values = []
    for association_id, item in lattice_vpc_associations(ctx).items():
        detail = ctx.call(
            LATTICE, 'get_service_network_vpc_association',
            serviceNetworkVpcAssociationIdentifier=item['id'])
        if (detail.get('id') != association_id or detail.get('arn') != item['arn']
                or detail.get('serviceNetworkId') != item['serviceNetworkId']
                or detail.get('serviceNetworkArn') != item['serviceNetworkArn']
                or detail.get('vpcId') != item.get('vpcId')
                or detail.get('status') != item['status']):
            raise NoData('VPC Lattice VPC association changed during collection')
        groups = detail.get('securityGroupIds', [])
        if (not isinstance(groups, list)
                or any(not isinstance(group, str) or not group.startswith('sg-')
                       for group in groups)
                or len(groups) != len(set(groups))):
            raise NoData('VPC Lattice VPC association has an invalid security-group inventory')
        values.append((item['arn'], len(groups), None))
    return maximum(values, 'VpcLatticeServiceNetworkVpcAssociation',
                   'vpc-lattice:ListServiceNetworkVpcAssociations+'
                   'GetServiceNetworkVpcAssociation')


def lattice_endpoints_per_network(ctx):
    values = []
    for network in service_networks(ctx).values():
        found = {}
        items = ctx.call(LATTICE, 'list_service_network_vpc_endpoint_associations',
                         'items', serviceNetworkIdentifier=network['id'])
        for item in items:
            if not isinstance(item, dict):
                raise NoData('VPC Lattice endpoint association inventory is invalid')
            identifier = item.get('id')
            endpoint = item.get('vpcEndpointId')
            owner = item.get('vpcEndpointOwnerId')
            state = item.get('state')
            if (not isinstance(identifier, str) or not identifier
                    or not isinstance(endpoint, str) or not endpoint.startswith('vpce-')
                    or not isinstance(owner, str) or len(owner) != 12 or not owner.isdigit()
                    or not isinstance(state, str) or not state
                    or item.get('serviceNetworkArn') != network['arn']):
                raise NoData('VPC Lattice endpoint association is inconsistent')
            if identifier in found:
                if found[identifier] != item:
                    raise NoData('VPC Lattice endpoint association changed during pagination')
                continue
            found[identifier] = item
        values.append((network['arn'], len(found), None))
    return maximum(values, 'VpcLatticeServiceNetwork',
                   'vpc-lattice:ListServiceNetworks+'
                   'ListServiceNetworkVpcEndpointAssociations')


def lattice_resource_configurations_per_network(ctx):
    values = []
    for network in service_networks(ctx).values():
        items = _inventory(
            ctx, 'list_service_network_resource_associations',
            'servicenetworkresourceassociation/', 'resource association',
            states=ASSOCIATION_STATES - {'UPDATE_IN_PROGRESS', 'UPDATE_FAILED'},
            counted=COUNTED_ASSOCIATION_STATES,
            serviceNetworkIdentifier=network['id'], includeChildren=True)
        configurations = set()
        for item in items.values():
            config_id = item.get('resourceConfigurationId')
            if (item.get('serviceNetworkId') != network['id']
                    or item.get('serviceNetworkArn') != network['arn']
                    or not isinstance(config_id, str) or not config_id):
                raise NoData('VPC Lattice resource association has an inconsistent parent')
            if config_id in configurations:
                raise NoData('VPC Lattice resource configuration has duplicate associations')
            configurations.add(config_id)
        values.append((network['arn'], len(configurations), None))
    return maximum(values, 'VpcLatticeServiceNetwork',
                   'vpc-lattice:ListServiceNetworks+'
                   'ListServiceNetworkResourceAssociations')


VPC_LATTICE_CHECKS = [
    ('L-9CAD07FB', 'Service networks per region',
     lambda ctx: account_count(service_networks(ctx),
                               'vpc-lattice:ListServiceNetworks')),
    ('L-620C821E', 'Services per region',
     lambda ctx: account_count(services(ctx), 'vpc-lattice:ListServices')),
    ('L-BB11C6B9', 'Target groups per region',
     lambda ctx: account_count(target_groups(ctx),
                               'vpc-lattice:ListTargetGroups')),
    ('L-D64E952E', 'Listeners per service', lattice_listeners_per_service),
    ('L-3DEC3B9F', 'Target groups per service', lattice_target_groups_per_service),
    ('L-CF78395E', 'Rules per listener', lattice_rules_per_listener),
    ('L-5FF8F9B9', 'Resource configurations per AWS Region',
     lambda ctx: account_count(resource_configurations(ctx),
                               'vpc-lattice:ListResourceConfigurations')),
    ('L-0DCA4434', 'Resource gateways per VPC',
     lattice_resource_gateways_per_vpc),
    ('L-6095700C', 'Resource Configurations per service network',
     lattice_resource_configurations_per_network),
    ('L-CA6A1CC5', 'Security groups per association',
     lattice_security_groups_per_association),
    ('L-75D4A19E', 'Service associations per service network',
     lattice_service_associations_per_network),
    ('L-73D0F278', 'Domain Verifications per AWS Region',
     lambda ctx: account_count(domain_verifications(ctx),
                               'vpc-lattice:ListDomainVerifications')),
    ('L-89DEA27F', "VPC endpoints of type 'service network' per service network",
     lattice_endpoints_per_network),
    ('L-9BC96FEF', 'Child Resource Configurations per Group Resource Configuration',
     lattice_children_per_group),
    ('L-D71303F3', 'Targets per target group', lattice_targets_per_target_group),
    ('L-EF6E2D62', 'VPC associations per service network',
     lattice_vpc_associations_per_network),
]

THINCLIENT_CHECKS = [
    ('L-64C2BDF4', 'Number of Environments',
     count('workspaces-thin-client', 'list_environments', 'environments')),
]

ALL_CHECKS = {'vpc-lattice': VPC_LATTICE_CHECKS, 'thinclient': THINCLIENT_CHECKS}


def get_current_quotastatus_new_services(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    entries = []
    for service, checks in ALL_CHECKS.items():
        selected = [check for check in checks
                    if (service, check[0]) in context.quotas]
        if selected:
            entries.extend(context.run(service, selected, skip))
    return entries
