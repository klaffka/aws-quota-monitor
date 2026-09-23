"""VPC accounting follows direction, address-family and resource scope limits."""
from collections import Counter, defaultdict
from datetime import timedelta
from modules.qmcore.aws import CheckContext, maximum, Unsupported, NoData, session_from_env
from modules.qmcore.metrics import fetch_metrics


def inventory(ctx, method, key, **kwargs):
    # Shared VPC visibility must not charge another account's resources to this account.
    if method in {'describe_vpcs', 'describe_security_groups', 'describe_network_interfaces',
                  'describe_subnets', 'describe_route_tables', 'describe_network_acls'}:
        kwargs['Filters'] = [*list(kwargs.get('Filters', [])), {'Name': 'owner-id', 'Values': [ctx.account]}]
    return ctx.call('ec2', method, key, **kwargs)


def grouped(items, field, resource_type='VPC'):
    counts = Counter(item[field] for item in items)
    return maximum([(key, count, None) for key, count in counts.items()], resource_type)


def prefix_info(ctx, prefix_id):
    lists = inventory(ctx, 'describe_managed_prefix_lists', 'PrefixLists', PrefixListIds=[prefix_id])
    if len(lists) != 1:
        raise NoData(f'Prefix list {prefix_id} not resolved')
    prefix = lists[0]
    family = prefix['AddressFamily']
    if prefix.get('OwnerId') != 'AWS':
        weight = prefix.get('MaxEntries')
        if isinstance(weight, (int, float)) and weight > 0:
            return family, weight
        raise Unsupported(f'Prefix list {prefix_id} has no valid MaxEntries')
    # Published AWS weights; unknown/new services are explicitly unsupported.
    name = prefix['PrefixListName']
    weights = {'cloudfront.origin-facing': 55, 'dynamodb': 1, 'ec2-instance-connect': 2,
               'groundstation': 5, 'route53-healthchecks': 25, 's3': 1,
               's3express': 6, 'secretsmanager-managed-external-secrets': 20, 'vpc-lattice': 10}
    for suffix, weight in weights.items():
        if name.endswith('.' + suffix):
            return family, weight
    # AWS-managed lists expose their effective weight in MaxEntries.  This
    # keeps newly introduced AWS lists measurable without guessing a name map.
    weight = prefix.get('MaxEntries')
    if isinstance(weight, (int, float)) and weight > 0:
        return family, weight
    raise Unsupported(f'Unknown AWS prefix list weight: {name}')


def security_group_rules(ctx):
    values = []
    for sg in inventory(ctx, 'describe_security_groups', 'SecurityGroups'):
        for direction, field in [('inbound', 'IpPermissions'), ('outbound', 'IpPermissionsEgress')]:
            counts = {'ipv4': 0, 'ipv6': 0}
            for permission in sg.get(field, []):
                counts['ipv4'] += len(permission.get('IpRanges', []))
                counts['ipv6'] += len(permission.get('Ipv6Ranges', []))
                for family in counts:
                    counts[family] += len(permission.get('UserIdGroupPairs', []))
                for prefix in permission.get('PrefixListIds', []):
                    family, weight = prefix_info(ctx, prefix['PrefixListId'])
                    counts[family] += weight
            values.extend((sg['GroupId'], value, {'direction': direction, 'addressFamily': family})
                          for family, value in counts.items())
    return maximum(values, 'SecurityGroup', 'ec2:DescribeSecurityGroups+DescribeManagedPrefixLists')


def acl_rules(ctx):
    values = []
    for acl in inventory(ctx, 'describe_network_acls', 'NetworkAcls'):
        for egress in (False, True):
            # The immutable catch-all deny entry (32767) does not consume a rule slot.
            count = sum(e['RuleNumber'] != 32767 and e['Egress'] == egress for e in acl.get('Entries', []))
            values.append((acl['NetworkAclId'], count, {'direction': 'outbound' if egress else 'inbound'}))
    return maximum(values, 'NetworkAcl', 'ec2:DescribeNetworkAcls')


def route_rules(ctx):
    values = []
    for table in inventory(ctx, 'describe_route_tables', 'RouteTables'):
        counts = {'ipv4': 0, 'ipv6': 0}
        for route in table.get('Routes', []):
            if route.get('Origin') == 'EnableVgwRoutePropagation':
                continue
            if 'DestinationPrefixListId' in route:
                family, weight = prefix_info(ctx, route['DestinationPrefixListId'])
            else:
                family, weight = ('ipv6' if 'DestinationIpv6CidrBlock' in route else 'ipv4'), 1
            counts[family] += weight
        values.extend((table['RouteTableId'], value, {'addressFamily': family}) for family, value in counts.items())
    return maximum(values, 'RouteTable', 'ec2:DescribeRouteTables+DescribeManagedPrefixLists')


def nat_gateways(ctx):
    return [n for n in inventory(ctx, 'describe_nat_gateways', 'NatGateways')
            if n['State'] in {'pending', 'available', 'deleting'}]


def nat_per_az(ctx):
    subnets = {s['SubnetId']: s['AvailabilityZone'] for s in ctx.call('ec2', 'describe_subnets', 'Subnets')}
    counts = Counter(subnets[n['SubnetId']] for n in nat_gateways(ctx))
    return maximum([(az, count, None) for az, count in counts.items()], 'AvailabilityZone', 'ec2:DescribeNatGateways')


def nat_per_vpc(ctx):
    subnets = {s['SubnetId']: s.get('VpcId') for s in ctx.call('ec2', 'describe_subnets', 'Subnets')}
    counts = Counter((n.get('VpcId') or subnets.get(n.get('SubnetId'))) for n in nat_gateways(ctx))
    counts.pop(None, None)
    return maximum([(vpc, count, None) for vpc, count in counts.items()], 'VPC', 'ec2:DescribeNatGateways')


def nat_addresses(ctx, field):
    return maximum([(n['NatGatewayId'], sum(bool(a.get(field)) for a in n.get('NatGatewayAddresses', [])), None)
                    for n in nat_gateways(ctx) if field != 'AllocationId' or n.get('ConnectivityType') == 'public'],
                   'NatGateway', 'ec2:DescribeNatGateways')


def endpoints(ctx, types):
    return [e for e in inventory(ctx, 'describe_vpc_endpoints', 'VpcEndpoints')
            if e.get('VpcEndpointType') in types and e.get('State') not in {'deleted', 'failed', 'rejected', 'expired'}]


def cidrs(ctx, version):
    field = 'CidrBlockAssociationSet' if version == 4 else 'Ipv6CidrBlockAssociationSet'
    state_field = 'CidrBlockState' if version == 4 else 'Ipv6CidrBlockState'
    return maximum([(v['VpcId'], sum(a.get(state_field, {}).get('State') in {'associated', 'associating', 'disassociating'}
                                     for a in v.get(field, [])), None)
                    for v in inventory(ctx, 'describe_vpcs', 'Vpcs')], 'VPC', 'ec2:DescribeVpcs')


def peerings(ctx, pending=False):
    local = {v['VpcId'] for v in inventory(ctx, 'describe_vpcs', 'Vpcs')}
    counts = Counter()
    for p in inventory(ctx, 'describe_vpc_peering_connections', 'VpcPeeringConnections'):
        if p.get('Status', {}).get('Code') != ('pending-acceptance' if pending else 'active'):
            continue
        sides = ['AccepterVpcInfo'] if pending else ['RequesterVpcInfo', 'AccepterVpcInfo']
        for side in sides:
            vid = p.get(side, {}).get('VpcId')
            if vid in local:
                counts[vid] += 1
    return maximum([(vid, count, None) for vid, count in counts.items()], 'VPC', 'ec2:DescribeVpcPeeringConnections')


def nau(ctx, metric_name):
    vpcs = inventory(ctx, 'describe_vpcs', 'Vpcs')
    if not vpcs:
        return maximum([], 'VPC', 'cloudwatch:AWS/EC2:' + metric_name)
    quotas = [dict(ServiceCode='vpc', QuotaCode=v['VpcId'], QuotaName=metric_name, Value=1, Unit='Count',
                   UsageMetric=dict(MetricNamespace='AWS/EC2', MetricName=metric_name,
                                    MetricStatisticRecommendation='Maximum', MetricDimensions={'VpcId': v['VpcId']}))
              for v in vpcs]
    entries = fetch_metrics(ctx, quotas, ctx.now - timedelta(minutes=20), ctx.now)
    if any(e['qualityStatus'] == 'ERROR' for e in entries):
        raise RuntimeError('Incomplete NAU CloudWatch inventory')
    if any(e['qualityStatus'] != 'OK' for e in entries):
        raise NoData('NAU metric missing for one or more VPCs; enable NAU metrics')
    return maximum([(e['quotaCode'], e['usageValue'], None) for e in entries], 'VPC', 'cloudwatch:AWS/EC2:' + metric_name)


def _ram_accounts(ctx, principal_id, seen=None):
    seen = seen or set()
    if principal_id in seen:
        return set()
    seen.add(principal_id)
    if principal_id.isdigit() and len(principal_id) == 12:
        return {principal_id}
    if principal_id.startswith('ou-'):
        accounts = {a['Id'] for a in ctx.call('organizations', 'list_accounts_for_parent', 'Accounts', ParentId=principal_id)}
        children = ctx.call('organizations', 'list_organizational_units_for_parent', 'OrganizationalUnits', ParentId=principal_id)
        for child in children:
            accounts.update(_ram_accounts(ctx, child['Id'], seen))
        return accounts
    if principal_id.startswith('o-'):
        accounts = set()
        for root in ctx.call('organizations', 'list_roots', 'Roots'):
            accounts.update(_ram_accounts(ctx, root['Id'], seen))
        return accounts
    raise Unsupported(f'Unsupported RAM principal scope: {principal_id}')


def participants(ctx):
    subnet_vpc = {s['SubnetId']: s['VpcId'] for s in inventory(ctx, 'describe_subnets', 'Subnets')}
    counts = defaultdict(set)
    resources = ctx.call('ram', 'list_resources', 'resources', resourceOwner='SELF', resourceType='ec2:Subnet')
    for resource in resources:
        subnet = resource['arn'].split('/')[-1]
        if subnet not in subnet_vpc:
            raise NoData('Shared subnet absent from VPC inventory')
        principals = ctx.call('ram', 'list_principals', 'principals', resourceOwner='SELF',
                              resourceShareArns=[resource['resourceShareArn']])
        for principal in principals:
            pid = principal['id']
            counts[subnet_vpc[subnet]].update(account for account in _ram_accounts(ctx, pid)
                                              if account != ctx.account)
    return maximum([(vid, len(accounts), None) for vid, accounts in counts.items()], 'VPC', 'ram:ListResources+ListPrincipals')


def sg_associations(ctx):
    associations = inventory(ctx, 'describe_security_group_vpc_associations', 'SecurityGroupVpcAssociations')
    counts = defaultdict(set)
    for association in associations:
        if association['State'] in {'associated', 'associating', 'disassociating', 'disassociation-failed'}:
            counts[association['GroupId']].add(association['VpcId'])
    return maximum([(gid, len(vpcs), None) for gid, vpcs in counts.items()], 'SecurityGroup', 'ec2:DescribeSecurityGroupVpcAssociations')


CHECKS = [
    ('L-F678F1CE', 'VPCs per Region', lambda c: dict(usage=len(inventory(c, 'describe_vpcs', 'Vpcs')))),
    ('L-A4707A72', 'Internet gateways per Region', lambda c: dict(usage=len(inventory(c, 'describe_internet_gateways', 'InternetGateways')))),
    ('L-45FE3B85', 'Egress-only internet gateways per Region', lambda c: dict(usage=len(inventory(c, 'describe_egress_only_internet_gateways', 'EgressOnlyInternetGateways')))),
    # The catalog defines this quota per Region at account level, so the busiest
    # Availability Zone is not the usage: the whole Region's interfaces are.
    ('L-DF5E4CA3', 'Network interfaces per Region',
     lambda c: dict(usage=len(inventory(c, 'describe_network_interfaces', 'NetworkInterfaces')),
                    source='ec2:DescribeNetworkInterfaces', method='ACCOUNT_COUNT')),
    ('L-E79EC296', 'VPC security groups per Region', lambda c: dict(usage=len(inventory(c, 'describe_security_groups', 'SecurityGroups')))),
    ('L-1B52E74A', 'Gateway VPC endpoints per Region', lambda c: dict(usage=len(endpoints(c, {'Gateway'})))),
    ('L-DC9F7029', 'Outstanding VPC peering connection requests per VPC', lambda c: peerings(c, True)),
    ('L-83CA0A9D', 'IPv4 CIDR blocks per VPC', lambda c: cidrs(c, 4)),
    ('L-085A6257', 'IPv6 CIDR blocks per VPC', lambda c: cidrs(c, 6)),
    ('L-B4A6D682', 'Network ACLs per VPC', lambda c: grouped(inventory(c, 'describe_network_acls', 'NetworkAcls'), 'VpcId')),
    ('L-589F43AA', 'Route tables per VPC', lambda c: grouped(inventory(c, 'describe_route_tables', 'RouteTables'), 'VpcId')),
    ('L-407747CB', 'Subnets per VPC', lambda c: grouped(inventory(c, 'describe_subnets', 'Subnets'), 'VpcId')),
    ('L-29B6F2EB', 'Interface and Gateway Load Balancer endpoints per VPC', lambda c: grouped(endpoints(c, {'Interface', 'GatewayLoadBalancer'}), 'VpcId')),
    ('L-7E9ECCDB', 'Active VPC peering connections per VPC', peerings),
    ('L-12E49864', 'NAT gateways per VPC', nat_per_vpc),
    ('L-CA6CC422', 'Resource endpoints per VPC', lambda c: grouped(endpoints(c, {'Resource'}), 'VpcId')),
    ('L-3B4E38D2', 'Service network endpoints per VPC', lambda c: grouped(endpoints(c, {'ServiceNetwork'}), 'VpcId')),
    ('L-FE5A380F', 'NAT gateways per Availability Zone', nat_per_az),
    ('L-0EA8095F', 'Inbound or outbound rules per security group', security_group_rules),
    ('L-93826ACB', 'Routes per route table', route_rules),
    ('L-2AEEBF1A', 'Rules per network ACL', acl_rules),
    ('L-2AFB9258', 'Security groups per network interface', lambda c: maximum(
        [(e['NetworkInterfaceId'], len(e.get('Groups', [])), None) for e in inventory(c, 'describe_network_interfaces', 'NetworkInterfaces')], 'NetworkInterface')),
    ('L-5F53652F', 'Elastic IP addresses per public NAT gateway', lambda c: nat_addresses(c, 'AllocationId')),
    ('L-DFA99DE7', 'Private IP addresses per NAT gateway', lambda c: nat_addresses(c, 'PrivateIp')),
    ('L-BB24F6E5', 'Network Address Usage', lambda c: nau(c, 'NetworkAddressUsage')),
    ('L-CD17FD4B', 'Peered Network Address Usage', lambda c: nau(c, 'NetworkAddressUsagePeered')),
    ('L-2C462E13', 'Participant accounts per VPC', participants),
    ('L-44499CD2', 'Subnets that can be shared with an account', lambda c: dict(usage=len({r['arn'] for r in c.call(
        'ram', 'list_resources', 'resources', resourceOwner='OTHER-ACCOUNTS', resourceType='ec2:Subnet')}))),
    ('L-A272D574', 'VPC associations per security group', sg_associations),
    # EC2 wants ExclusionIds or MaxResults; the page size lets the NextToken loop walk them all.
    ('L-42B9C2CA', 'VPC Block Public Access exclusions per account per Region', lambda c: dict(usage=sum(
        e['State'] not in {'delete-complete', 'create-failed'} for e in inventory(
            c, 'describe_vpc_block_public_access_exclusions', 'VpcBlockPublicAccessExclusions', MaxResults=1000)))),
]


def get_current_quotastatus_vpc(session=None, *, ctx=None, skip=()):
    return (ctx or CheckContext(session or session_from_env())).run('vpc', CHECKS, skip)
