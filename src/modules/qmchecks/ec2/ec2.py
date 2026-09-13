"""EC2 quotas measured from complete resource inventories."""
from functools import partial
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env
from modules.qmchecks.ec2.host_families import HOST_FAMILIES


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


def capacity_blocks(ctx, instance_type):
    reservations = ctx.call('ec2', 'describe_capacity_reservations', 'CapacityReservations')
    blocks = {r.get('CapacityBlockId') or r['CapacityReservationId'] for r in reservations
              if r.get('ReservationType') == 'capacity-block' and r.get('State') == 'active'
              and r.get('InstanceType') == instance_type and r.get('OwnerId') == ctx.account
              and (not r.get('StartDate') or r['StartDate'] <= ctx.now)
              and (not r.get('EndDate') or ctx.now < r['EndDate'])}
    return dict(usage=len(blocks), source='ec2:DescribeCapacityReservations',
                meta={'activeCapacityBlockIds': sorted(blocks)}, method='ACTIVE_BLOCK_COUNT')


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
    ('L-2C8F52B3', 'Concurrent P4d Capacity Blocks per account', lambda c: capacity_blocks(c, 'p4d.24xlarge')),
    ('L-CFF3E941', 'Concurrent P4de Capacity Blocks per account', lambda c: capacity_blocks(c, 'p4de.24xlarge')),
]

HOST_CHECKS = [(code, f'Running Dedicated {family} Hosts', partial(dedicated_hosts, family=family))
               for code, family in HOST_FAMILIES.items()]
ALL_CHECKS = CHECKS + HOST_CHECKS


def get_current_quotastatus_ec2(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    # Only request family quotas that this account/Region actually advertises.
    checks = CHECKS + [check for check in HOST_CHECKS if ('ec2', check[0]) in context.quotas]
    return context.run('ec2', checks, skip)
