"""EC2 quotas measured from complete resource inventories."""
from functools import partial
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env
from modules.qmchecks.ec2.host_families import HOST_FAMILIES

CLIENT_VPN_CONNECTION_STATES = {'active', 'failed-to-terminate', 'terminating',
                                'terminated'}
# Capacity block quotas per instance family, as the catalog names them.
CAPACITY_BLOCK_FAMILIES = (
    ('L-2C8F52B3', 'P4d', 'p4d'), ('L-CFF3E941', 'P4de', 'p4de'),
    ('L-DA6814F2', 'P5', 'p5'), ('L-C45F30BC', 'P5e', 'p5e'),
    ('L-4F9BB70B', 'P5en', 'p5en'), ('L-8B23CEF3', 'P6-B200', 'p6-b200'),
    ('L-9C38E5AB', 'P6-B300', 'p6-b300'),
    ('L-FCF0179E', 'P6e-GB200', 'p6e-gb200'),
    ('L-2E30FD7D', 'TRN1', 'trn1'), ('L-64569A79', 'TRN2', 'trn2'),
)


def ami_sharing(ctx):
    images = ctx.call('ec2', 'describe_images', 'Images', Owners=['self'])
    values = []
    for image in images:
        permissions = ctx.call('ec2', 'describe_image_attribute', ImageId=image['ImageId'],
                               Attribute='launchPermission').get('LaunchPermissions', [])
        counts = {key: len({p[key] for p in permissions if key in p})
                  for key in ('UserId', 'OrganizationArn', 'OrganizationalUnitArn')}
        # Public access is not a shared account, organization or OU.
        values.append((image['ImageId'], sum(counts.values()), counts))
    return maximum(values, 'AMI', 'ec2:DescribeImages+DescribeImageAttribute')


def images(ctx):
    """Return all AMIs owned by this account, including private images.

    ``describe_images`` is paginated by CheckContext and the owner filter is
    important: without it the result would be an arbitrary public catalogue.
    """
    return ctx.call('ec2', 'describe_images', 'Images', Owners=['self'])


def ami_count(ctx):
    live = {image['ImageId'] for image in images(ctx)}
    # The EC2 AMI quota includes images in the Recycle Bin.  Keep this
    # inventory separate from ``images`` because recycle-bin entries have no
    # launch permissions and therefore must not affect AMI-sharing checks.
    recycled = {entry['ImageId'] for entry in ctx.call(
        'ec2', 'list_images_in_recycle_bin', 'Images')
                if entry.get('ImageId')}
    return dict(usage=len(live | recycled), source='ec2:DescribeImages+ListImagesInRecycleBin',
                method='ACCOUNT_COUNT')


def public_ami_count(ctx):
    count = 0
    for image in images(ctx):
        permissions = ctx.call('ec2', 'describe_image_attribute', ImageId=image['ImageId'],
                               Attribute='launchPermission').get('LaunchPermissions', [])
        count += any(permission.get('Group') == 'all' for permission in permissions)
    return dict(usage=count, source='ec2:DescribeImages+DescribeImageAttribute', method='ACCOUNT_COUNT')


def launch_templates(ctx):
    return ctx.call('ec2', 'describe_launch_templates', 'LaunchTemplates', OwnerId=ctx.account)


def launch_template_count(ctx):
    return dict(usage=len(launch_templates(ctx)), source='ec2:DescribeLaunchTemplates', method='ACCOUNT_COUNT')


def launch_template_versions(ctx):
    values = []
    for template in launch_templates(ctx):
        versions = ctx.call('ec2', 'describe_launch_template_versions', 'LaunchTemplateVersions',
                            LaunchTemplateId=template['LaunchTemplateId'])
        values.append((template['LaunchTemplateId'], len(versions), None))
    return maximum(values, 'LaunchTemplate', 'ec2:DescribeLaunchTemplateVersions')


def elastic_ip_count(ctx):
    """Count allocated VPC Elastic IPs, which consume the regional quota."""
    addresses = ctx.call('ec2', 'describe_addresses', 'Addresses')
    return dict(usage=sum(address.get('Domain') == 'vpc' for address in addresses),
                source='ec2:DescribeAddresses', method='ACCOUNT_COUNT')


def verified_access_count(ctx, method, key):
    return dict(usage=len(ctx.call('ec2', method, key)), source=f'ec2:{method}', method='ACCOUNT_COUNT')

def ec2_resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('ec2', method, key)), source=f'ec2:{method}', method='ACCOUNT_COUNT')


def vpn_endpoints(ctx):
    return ctx.call('ec2', 'describe_client_vpn_endpoints', 'ClientVpnEndpoints')


def vpn_connections(ctx):
    return ctx.call('ec2', 'describe_vpn_connections', 'VpnConnections')


def vpn_connections_per_vgw(ctx):
    connections = vpn_connections(ctx)
    from collections import Counter
    counts = Counter(c.get('VpnGatewayId') for c in connections if c.get('VpnGatewayId'))
    gateway, usage = max(counts.items(), key=lambda item: item[1], default=(None, 0))
    return dict(usage=usage, resource_type='VirtualPrivateGateway', resource_id=gateway,
                source='ec2:DescribeVpnConnections', method='PER_RESOURCE_MAX')


def vpn_rules(ctx):
    values = [(e['ClientVpnEndpointId'], len(ctx.call('ec2', 'describe_client_vpn_authorization_rules',
               'AuthorizationRules', ClientVpnEndpointId=e['ClientVpnEndpointId'])), None)
              for e in vpn_endpoints(ctx)]
    return maximum(values, 'ClientVpnEndpoint', 'ec2:DescribeClientVpnAuthorizationRules')


def client_vpn_connections(ctx):
    """Count the sessions an endpoint is currently carrying."""
    values = []
    for endpoint in vpn_endpoints(ctx):
        identity = endpoint['ClientVpnEndpointId']
        usage = 0
        for connection in ctx.call('ec2', 'describe_client_vpn_connections',
                                   'Connections', ClientVpnEndpointId=identity):
            status = (connection.get('Status') or {}).get('Code')
            if status not in CLIENT_VPN_CONNECTION_STATES:
                raise NoData('Client VPN connection has an unknown status')
            usage += status == 'active'
        values.append((identity, usage, None))
    return maximum(values, 'ClientVpnEndpoint', 'ec2:DescribeClientVpnConnections')


def client_vpn_routes_per_association(ctx):
    counts = {}
    for endpoint in vpn_endpoints(ctx):
        identity = endpoint['ClientVpnEndpointId']
        for route in ctx.call('ec2', 'describe_client_vpn_routes', 'Routes',
                              ClientVpnEndpointId=identity):
            subnet = route.get('TargetSubnet')
            if not subnet:
                raise NoData('Client VPN route names no target network')
            key = f'{identity}/{subnet}'
            counts[key] = counts.get(key, 0) + 1
    return maximum(((key, count, None) for key, count in counts.items()),
                   'ClientVpnTargetNetwork', 'ec2:DescribeClientVpnRoutes')


def capacity_blocks(ctx, family):
    """Count this account's active capacity blocks of one instance family.

    The quotas name a family ("P5", "TRN2"), not one size, so the family is
    matched against the part of the instance type before the dot.
    """
    reservations = ctx.call('ec2', 'describe_capacity_reservations', 'CapacityReservations')
    blocks = {r.get('CapacityBlockId') or r['CapacityReservationId'] for r in reservations
              if r.get('ReservationType') == 'capacity-block' and r.get('State') == 'active'
              and str(r.get('InstanceType', '')).split('.')[0] == family
              and r.get('OwnerId') == ctx.account
              and (not r.get('StartDate') or r['StartDate'] <= ctx.now)
              and (not r.get('EndDate') or ctx.now < r['EndDate'])}
    return dict(usage=len(blocks), source='ec2:DescribeCapacityReservations',
                meta={'instanceFamily': family, 'activeCapacityBlockIds': sorted(blocks)},
                method='ACTIVE_BLOCK_COUNT')


def dedicated_hosts(ctx, family):
    """Count allocated regional hosts, independently of guest instance occupancy.

    DescribeHosts includes recently released and shared hosts. Family metadata
    supports both single-size hosts and hosts allowing multiple instance sizes.
    Recovery/maintenance may temporarily expose a replacement and its original;
    do not claim a precise quota count until those hosts reach a stable state.
    """
    hosts = set()
    for host in ctx.call('ec2', 'describe_hosts', 'Hosts'):
        if host.get('State') in {'released', 'released-permanent-failure'}:
            continue
        if not host.get('OwnerId'):
            raise NoData('Dedicated host inventory is missing the owner account')
        if host['OwnerId'] != ctx.account:
            continue
        properties = host.get('HostProperties') or {}
        host_family = properties.get('InstanceFamily')
        if not host_family:
            instance_type = properties.get('InstanceType', '')
            host_family = instance_type.split('.')[0] if '.' in instance_type else None
        if not host_family:
            raise NoData('Dedicated host inventory is missing the instance family')
        if host_family != family:
            continue
        if host.get('OutpostArn'):
            raise NoData('Outpost dedicated hosts need a separate quota scope')
        if host.get('State') != 'available':
            raise NoData(f"Dedicated host {host.get('HostId')} is in transitional or impaired state: {host.get('State')}")
        if not host.get('HostId'):
            raise NoData('Dedicated host inventory is missing the host ID')
        hosts.add(host['HostId'])
    return dict(usage=len(hosts), source='ec2:DescribeHosts', method='ACCOUNT_COUNT',
                meta={'instanceFamily': family})


def multicast_domains(ctx):
    """Return each multicast domain with the transit gateway that owns it."""
    found = {}
    for domain in ctx.call('ec2', 'describe_transit_gateway_multicast_domains',
                           'TransitGatewayMulticastDomains'):
        identity = domain.get('TransitGatewayMulticastDomainId')
        gateway = domain.get('TransitGatewayId')
        if not identity or not gateway:
            raise NoData('Multicast domain is missing its identity or gateway')
        if domain.get('State') == 'deleted':
            continue
        found[identity] = gateway
    return found


def multicast_domains_per_gateway(ctx):
    counts = {}
    for gateway in multicast_domains(ctx).values():
        counts[gateway] = counts.get(gateway, 0) + 1
    return maximum(((gateway, count, None) for gateway, count in counts.items()),
                   'TransitGateway',
                   'ec2:DescribeTransitGatewayMulticastDomains')


def multicast_groups(ctx):
    """Yield every multicast group entry with the domain it belongs to."""
    for identity, gateway in multicast_domains(ctx).items():
        for group in ctx.call('ec2', 'search_transit_gateway_multicast_groups',
                              'MulticastGroups',
                              TransitGatewayMulticastDomainId=identity):
            address = group.get('GroupIpAddress')
            if not address:
                raise NoData('Multicast group entry has no group address')
            yield identity, gateway, address, group


def _group_members(field):
    """Count the sources or the members of the busiest multicast group."""
    def check(ctx):
        counts = {}
        for identity, _, address, group in multicast_groups(ctx):
            if group.get(field):
                key = f'{identity}/{address}'
                counts[key] = counts.get(key, 0) + 1
        return maximum(((key, count, None) for key, count in counts.items()),
                       'TransitGatewayMulticastGroup',
                       'ec2:SearchTransitGatewayMulticastGroups')
    return check


def multicast_interfaces_per_gateway(ctx):
    interfaces = {}
    for _, gateway, _, group in multicast_groups(ctx):
        interface = group.get('NetworkInterfaceId')
        if interface:
            interfaces.setdefault(gateway, set()).add(interface)
    return maximum(((gateway, len(found), None)
                    for gateway, found in interfaces.items()),
                   'TransitGateway',
                   'ec2:SearchTransitGatewayMulticastGroups')


def multicast_associations_per_vpc(ctx):
    counts = {}
    for identity in multicast_domains(ctx):
        for association in ctx.call(
                'ec2', 'get_transit_gateway_multicast_domain_associations',
                'MulticastDomainAssociations',
                TransitGatewayMulticastDomainId=identity):
            if association.get('ResourceType') != 'vpc':
                continue
            vpc = association.get('ResourceId')
            if not vpc:
                raise NoData('Multicast domain association has no resource')
            counts[vpc] = counts.get(vpc, 0) + 1
    return maximum(((vpc, count, None) for vpc, count in counts.items()),
                   'Vpc', 'ec2:GetTransitGatewayMulticastDomainAssociations')


def transit_gateway_attachments(ctx, resource_type):
    """Group live transit gateway attachments of one kind by both ends."""
    per_gateway, per_resource = {}, {}
    for attachment in ctx.call('ec2', 'describe_transit_gateway_attachments',
                               'TransitGatewayAttachments'):
        if attachment.get('State') in {'deleted', 'deleting', 'failed', 'rejected'}:
            continue
        if attachment.get('ResourceType') != resource_type:
            continue
        gateway, resource = (attachment.get('TransitGatewayId'),
                             attachment.get('ResourceId'))
        if not gateway or not resource:
            raise NoData('Transit gateway attachment is missing an endpoint')
        per_gateway[gateway] = per_gateway.get(gateway, 0) + 1
        per_resource[resource] = per_resource.get(resource, 0) + 1
    return per_gateway, per_resource


def _attachments(resource_type, side, resource_label):
    def check(ctx):
        per_gateway, per_resource = transit_gateway_attachments(ctx, resource_type)
        counts = per_gateway if side == 'gateway' else per_resource
        return maximum(((key, count, None) for key, count in counts.items()),
                       resource_label, 'ec2:DescribeTransitGatewayAttachments')
    return check


CHECKS = [
    ('L-B665C33B', 'AMIs', ami_count),
    ('L-0E3CBAB9', 'Public AMIs', public_ami_count),
    ('L-70015FFA', 'AMI sharing', ami_sharing),
    ('L-FB451C26', 'Launch templates', launch_template_count),
    ('L-142B4294', 'Launch template versions', launch_template_versions),
    ('L-0263D0A3', 'EC2-VPC Elastic IPs', elastic_ip_count),
    ('L-17A8BD20', 'Verified Access instances',
     lambda c: verified_access_count(c, 'describe_verified_access_instances', 'VerifiedAccessInstances')),
    ('L-3829BC77', 'Verified Access groups',
     lambda c: verified_access_count(c, 'describe_verified_access_groups', 'VerifiedAccessGroups')),
    ('L-AF309E5E', 'Verified Access trust providers',
     lambda c: verified_access_count(c, 'describe_verified_access_trust_providers', 'VerifiedAccessTrustProviders')),
    ('L-A2478D36', 'Transit gateways per account', lambda c: ec2_resource_count(c, 'describe_transit_gateways', 'TransitGateways')),
    ('L-4FB7FF5D', 'Customer gateways per region', lambda c: ec2_resource_count(c, 'describe_customer_gateways', 'CustomerGateways')),
    ('L-7029FAB6', 'Virtual private gateways per region', lambda c: ec2_resource_count(c, 'describe_vpn_gateways', 'VpnGateways')),
    ('L-9A1BC94B', 'Authorization rules per Client VPN endpoint', vpn_rules),
    ('L-8EA77D34', 'Client VPN endpoints', lambda c: dict(usage=len(vpn_endpoints(c)), source='ec2:DescribeClientVpnEndpoints')),
    ('L-3E6EC3A3', 'VPN connections per region', lambda c: dict(usage=len(vpn_connections(c)), source='ec2:DescribeVpnConnections', method='ACCOUNT_COUNT')),
    ('L-B91E5754', 'VPN connections per VGW', vpn_connections_per_vgw),
    *[(code, f'Concurrent {label} Capacity Blocks per account',
       partial(capacity_blocks, family=family))
      for code, label, family in CAPACITY_BLOCK_FAMILIES],
    ('L-C4B238BF', 'Concurrent client connections per Client VPN endpoint',
     client_vpn_connections),
    ('L-401D78F7', 'Routes per Client VPN target network association',
     client_vpn_routes_per_association),
    ('L-5D439CF7', 'Verified Access Endpoints',
     lambda c: verified_access_count(c, 'describe_verified_access_endpoints',
                                     'VerifiedAccessEndpoints')),
    ('L-8FBBDF0C', 'Amazon FPGA images (AFIs)',
     lambda c: dict(usage=len(c.call('ec2', 'describe_fpga_images', 'FpgaImages',
                                     Owners=['self'])),
                    source='ec2:DescribeFpgaImages', method='ACCOUNT_COUNT')),
    ('L-31775423', 'Multicast domains per transit gateway',
     multicast_domains_per_gateway),
    ('L-4F2F99E3', 'Sources per transit gateway multicast group',
     _group_members('GroupSource')),
    ('L-C768F2D6', 'Members per transit gateway multicast group',
     _group_members('GroupMember')),
    ('L-C673935A', 'Multicast Network Interfaces per transit gateway',
     multicast_interfaces_per_gateway),
    ('L-9F8FA74B', 'Multicast domain associations per VPC',
     multicast_associations_per_vpc),
    ('L-350B2172', 'Direct Connect gateways per transit gateway',
     _attachments('direct-connect-gateway', 'gateway', 'TransitGateway')),
    ('L-6B192186', 'Transit gateways per Direct Connect Gateway',
     _attachments('direct-connect-gateway', 'resource', 'DirectConnectGateway')),
    ('L-6DA43717', 'Attachments per VPC', _attachments('vpc', 'resource', 'Vpc')),
]

HOST_CHECKS = [(code, f'Running Dedicated {family} Hosts', partial(dedicated_hosts, family=family))
               for code, family in HOST_FAMILIES.items()]
ALL_CHECKS = CHECKS + HOST_CHECKS


def get_current_quotastatus_ec2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    # Only request family quotas that this account/Region actually advertises.
    checks = CHECKS + [check for check in HOST_CHECKS if ('ec2', check[0]) in context.quotas]
    return context.run('ec2', checks, skip)
