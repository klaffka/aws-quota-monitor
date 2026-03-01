import boto3
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────

def _paginate(ec2_client, method_name, result_key, **kwargs):
    """Generic paginator that collects all results across pages."""
    paginator = ec2_client.get_paginator(method_name)
    results = []
    for page in paginator.paginate(**kwargs):
        results.extend(page.get(result_key, []))
    return results


def _get_limit(sq_client, quota_code):
    """Get the applied quota limit from Service Quotas API."""
    resp = sq_client.get_service_quota(ServiceCode='vpc', QuotaCode=quota_code)
    return resp['Quota']['Value']


def _fetch_all_limits(sq_client, service_code='vpc'):
    """Batch-fetch all quota limits for a service via ListServiceQuotas.

    Returns a dict mapping QuotaCode → applied Value.
    This replaces many individual GetServiceQuota calls with a single
    paginated list call, avoiding TooManyRequestsException.
    """
    limits = {}
    try:
        paginator = sq_client.get_paginator('list_service_quotas')
        for page in paginator.paginate(ServiceCode=service_code):
            for q in page.get('Quotas', []):
                limits[q['QuotaCode']] = q['Value']
    except Exception as e:
        logger.warning(f"Failed to batch-fetch limits for {service_code}: {e}")
    return limits


def _build_entry(account_id, region, collected_at, *,
                 quota_code, quota_name, limit_value, usage_value,
                 unit='Count', collector_type='REGION_TOTAL',
                 data_source='', calculation_method='REGION_TOTAL',
                 max_resource_type=None, max_resource_id=None,
                 max_resource_meta=None):
    """Build a standardised quota entry dict."""
    utilization_pct = round(usage_value / limit_value * 100, 2) if limit_value > 0 else 0
    return {
        'PK': f"QUOTA#{account_id}#vpc#{quota_code}",
        'SK': f"TS#{collected_at}",
        'accountId': account_id,
        'region': region,
        'serviceCode': 'vpc',
        'quotaCode': quota_code,
        'quotaName': quota_name,
        'scopeType': 'ACCOUNT_REGION',
        'limitValue': limit_value,
        'usageValue': usage_value,
        'utilizationPct': utilization_pct,
        'unit': unit,
        'collectorType': collector_type,
        'dataSource': data_source,
        'calculationMethod': calculation_method,
        'maxResourceType': max_resource_type,
        'maxResourceId': max_resource_id,
        'maxResourceMeta': max_resource_meta,
        'collectedAt': collected_at,
        'ttl': int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    }


def _max_per_group(items, group_key, count_fn=None):
    """Group items and return (max_group_id, max_count).

    *count_fn* – optional callable(group_id, items_in_group) → int.
    If omitted, the length of the group is used.
    """
    groups = defaultdict(list)
    for item in items:
        gid = item.get(group_key) if isinstance(group_key, str) else group_key(item)
        if gid:
            groups[gid].append(item)
    if not groups:
        return None, 0
    if count_fn:
        counts = {gid: count_fn(gid, grp) for gid, grp in groups.items()}
    else:
        counts = {gid: len(grp) for gid, grp in groups.items()}
    max_id = max(counts, key=counts.get)
    return max_id, counts[max_id]


# ── Main entry point ──────────────────────────────────────────────────────

def get_current_quotastatus_vpc(session=None):
    """Collect quota usage for Amazon VPC (service code: vpc).

    Returns a list of quota entry dicts ready for DynamoDB storage.
    Quotas covered by CloudWatch UsageMetric are skipped here
    (the reporting function fetches those directly).
    """
    vpc_quotas = []
    if session is None:
        session = boto3.Session()

    collected_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    account_id = session.client('sts').get_caller_identity().get('Account')
    region = session.region_name
    ec2 = session.client('ec2')
    sq = session.client('service-quotas')

    # ── Batch-fetch all VPC quota limits (single paginated call) ──────
    limits = _fetch_all_limits(sq, 'vpc')
    def get_limit(quota_code):
        """Look up limit from pre-fetched map, fall back to individual API call."""
        if quota_code in limits:
            return limits[quota_code]
        # Fallback for quotas not returned by ListServiceQuotas
        return _get_limit(sq, quota_code)

    # ── Pre-fetch resource inventory (paginated) ──────────────────────
    logger.info("VPC collector: fetching resource inventory")
    vpcs = _paginate(ec2, 'describe_vpcs', 'Vpcs')
    sgs = _paginate(ec2, 'describe_security_groups', 'SecurityGroups')
    nacls = _paginate(ec2, 'describe_network_acls', 'NetworkAcls')
    rts = _paginate(ec2, 'describe_route_tables', 'RouteTables')
    subnets = _paginate(ec2, 'describe_subnets', 'Subnets')
    enis = _paginate(ec2, 'describe_network_interfaces', 'NetworkInterfaces')
    igws = _paginate(ec2, 'describe_internet_gateways', 'InternetGateways')
    eigws = _paginate(ec2, 'describe_egress_only_internet_gateways',
                      'EgressOnlyInternetGateways')
    endpoints = _paginate(ec2, 'describe_vpc_endpoints', 'VpcEndpoints')
    nat_gws = _paginate(ec2, 'describe_nat_gateways', 'NatGateways',
                        Filters=[{'Name': 'state', 'Values': ['available']}])
    active_peerings = _paginate(ec2, 'describe_vpc_peering_connections',
                                'VpcPeeringConnections',
                                Filters=[{'Name': 'status-code', 'Values': ['active']}])
    pending_peerings = _paginate(ec2, 'describe_vpc_peering_connections',
                                 'VpcPeeringConnections',
                                 Filters=[{'Name': 'status-code',
                                           'Values': ['pending-acceptance']}])

    logger.info(f"VPC collector: {len(vpcs)} VPCs, {len(sgs)} SGs, "
                f"{len(nacls)} NACLs, {len(rts)} RTs, {len(subnets)} subnets, "
                f"{len(enis)} ENIs, {len(endpoints)} endpoints, "
                f"{len(nat_gws)} NAT GWs")

    # Shorthand for building entries
    def entry(**kw):
        return _build_entry(account_id, region, collected_at, **kw)

    # ══════════════════════════════════════════════════════════════════
    #  REGION-LEVEL CHECKS
    # ══════════════════════════════════════════════════════════════════

    # L-F678F1CE  VPCs per Region
    try:
        vpc_quotas.append(entry(
            quota_code='L-F678F1CE', quota_name='VPCs per Region',
            limit_value=get_limit('L-F678F1CE'), usage_value=len(vpcs),
            data_source='ec2:DescribeVpcs'))
    except Exception as e:
        logger.warning(f"VPC check L-F678F1CE failed: {e}")

    # L-A4707A72  Internet gateways per Region
    try:
        vpc_quotas.append(entry(
            quota_code='L-A4707A72', quota_name='Internet gateways per Region',
            limit_value=get_limit('L-A4707A72'), usage_value=len(igws),
            data_source='ec2:DescribeInternetGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-A4707A72 failed: {e}")

    # L-45FE3B85  Egress-only internet gateways per Region
    try:
        vpc_quotas.append(entry(
            quota_code='L-45FE3B85',
            quota_name='Egress-only internet gateways per Region',
            limit_value=get_limit('L-45FE3B85'), usage_value=len(eigws),
            data_source='ec2:DescribeEgressOnlyInternetGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-45FE3B85 failed: {e}")

    # L-DF5E4CA3  Network interfaces per Region
    try:
        vpc_quotas.append(entry(
            quota_code='L-DF5E4CA3', quota_name='Network interfaces per Region',
            limit_value=get_limit('L-DF5E4CA3'), usage_value=len(enis),
            data_source='ec2:DescribeNetworkInterfaces'))
    except Exception as e:
        logger.warning(f"VPC check L-DF5E4CA3 failed: {e}")

    # L-E79EC296  VPC security groups per Region
    try:
        vpc_quotas.append(entry(
            quota_code='L-E79EC296', quota_name='VPC security groups per Region',
            limit_value=get_limit('L-E79EC296'), usage_value=len(sgs),
            data_source='ec2:DescribeSecurityGroups'))
    except Exception as e:
        logger.warning(f"VPC check L-E79EC296 failed: {e}")

    # L-1B52E74A  Gateway VPC endpoints per Region
    try:
        gw_endpoints = [e for e in endpoints if e.get('VpcEndpointType') == 'Gateway']
        vpc_quotas.append(entry(
            quota_code='L-1B52E74A',
            quota_name='Gateway VPC endpoints per Region',
            limit_value=get_limit('L-1B52E74A'), usage_value=len(gw_endpoints),
            data_source='ec2:DescribeVpcEndpoints'))
    except Exception as e:
        logger.warning(f"VPC check L-1B52E74A failed: {e}")

    # L-DC9F7029  Outstanding VPC peering connection requests
    try:
        vpc_quotas.append(entry(
            quota_code='L-DC9F7029',
            quota_name='Outstanding VPC peering connection requests',
            limit_value=get_limit('L-DC9F7029'),
            usage_value=len(pending_peerings),
            data_source='ec2:DescribeVpcPeeringConnections'))
    except Exception as e:
        logger.warning(f"VPC check L-DC9F7029 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  PER-VPC CHECKS  (report VPC with highest usage)
    # ══════════════════════════════════════════════════════════════════

    # L-83CA0A9D  IPv4 CIDR blocks per VPC
    try:
        limit = get_limit('L-83CA0A9D')
        per_vpc = {v['VpcId']: len(v.get('CidrBlockAssociationSet', [])) for v in vpcs}
        if per_vpc:
            max_id = max(per_vpc, key=per_vpc.get)
            max_usage = per_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-83CA0A9D', quota_name='IPv4 CIDR blocks per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeVpcs'))
    except Exception as e:
        logger.warning(f"VPC check L-83CA0A9D failed: {e}")

    # L-085A6257  IPv6 CIDR blocks per VPC
    try:
        limit = get_limit('L-085A6257')
        per_vpc = {v['VpcId']: len(v.get('Ipv6CidrBlockAssociationSet', [])) for v in vpcs}
        if per_vpc:
            max_id = max(per_vpc, key=per_vpc.get)
            max_usage = per_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-085A6257', quota_name='IPv6 CIDR blocks per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeVpcs'))
    except Exception as e:
        logger.warning(f"VPC check L-085A6257 failed: {e}")

    # L-B4A6D682  Network ACLs per VPC
    try:
        limit = get_limit('L-B4A6D682')
        max_id, max_usage = _max_per_group(nacls, 'VpcId')
        vpc_quotas.append(entry(
            quota_code='L-B4A6D682', quota_name='Network ACLs per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeNetworkAcls'))
    except Exception as e:
        logger.warning(f"VPC check L-B4A6D682 failed: {e}")

    # L-589F43AA  Route tables per VPC
    try:
        limit = get_limit('L-589F43AA')
        max_id, max_usage = _max_per_group(rts, 'VpcId')
        vpc_quotas.append(entry(
            quota_code='L-589F43AA', quota_name='Route tables per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeRouteTables'))
    except Exception as e:
        logger.warning(f"VPC check L-589F43AA failed: {e}")

    # L-407747CB  Subnets per VPC
    try:
        limit = get_limit('L-407747CB')
        max_id, max_usage = _max_per_group(subnets, 'VpcId')
        vpc_quotas.append(entry(
            quota_code='L-407747CB', quota_name='Subnets per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeSubnets'))
    except Exception as e:
        logger.warning(f"VPC check L-407747CB failed: {e}")

    # L-29B6F2EB  Interface VPC endpoints per VPC
    #  → Has official UsageMetric (AWS/Usage namespace, ResourceCount).
    #    Reporting fetches this directly via CloudWatch get_metric_data.
    #    Not implemented in collector to maintain architecture separation.

    # L-7E9ECCDB  Active VPC peering connections per VPC
    try:
        limit = get_limit('L-7E9ECCDB')
        # A peering counts for both requester and accepter VPC
        peering_counts = defaultdict(int)
        for p in active_peerings:
            req_vpc = p.get('RequesterVpcInfo', {}).get('VpcId')
            acc_vpc = p.get('AccepterVpcInfo', {}).get('VpcId')
            if req_vpc:
                peering_counts[req_vpc] += 1
            if acc_vpc:
                peering_counts[acc_vpc] += 1
        if peering_counts:
            max_id = max(peering_counts, key=peering_counts.get)
            max_usage = peering_counts[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-7E9ECCDB',
            quota_name='Active VPC peering connections per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeVpcPeeringConnections'))
    except Exception as e:
        logger.warning(f"VPC check L-7E9ECCDB failed: {e}")

    # L-12E49864  NAT gateways per VPC  (regional count grouped by VPC)
    try:
        limit = get_limit('L-12E49864')
        # Group NAT gateways by the VPC they belong to
        nat_by_vpc = defaultdict(int)
        for ng in nat_gws:
            nat_by_vpc[ng.get('VpcId')] += 1
        if nat_by_vpc:
            max_id = max(nat_by_vpc, key=nat_by_vpc.get)
            max_usage = nat_by_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-12E49864', quota_name='NAT gateways per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeNatGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-12E49864 failed: {e}")

    # L-CA6CC422  VPC endpoints of type 'resource' per VPC
    try:
        limit = get_limit('L-CA6CC422')
        resource_eps = [e for e in endpoints if e.get('VpcEndpointType') == 'Resource']
        max_id, max_usage = _max_per_group(resource_eps, 'VpcId')
        vpc_quotas.append(entry(
            quota_code='L-CA6CC422',
            quota_name="VPC endpoints of type 'resource' per VPC",
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeVpcEndpoints'))
    except Exception as e:
        logger.warning(f"VPC check L-CA6CC422 failed: {e}")

    # L-3B4E38D2  VPC endpoints of type 'service network' per VPC
    try:
        limit = get_limit('L-3B4E38D2')
        sn_eps = [e for e in endpoints if e.get('VpcEndpointType') == 'ServiceNetwork']
        max_id, max_usage = _max_per_group(sn_eps, 'VpcId')
        vpc_quotas.append(entry(
            quota_code='L-3B4E38D2',
            quota_name="VPC endpoints of type 'service network' per VPC",
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ec2:DescribeVpcEndpoints'))
    except Exception as e:
        logger.warning(f"VPC check L-3B4E38D2 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  PER-AZ CHECK
    # ══════════════════════════════════════════════════════════════════

    # L-FE5A380F  NAT gateways per Availability Zone
    try:
        limit = get_limit('L-FE5A380F')
        # Group NAT gateways by subnet → AZ
        # NAT gateways have SubnetId; map subnet → AZ
        subnet_az = {s['SubnetId']: s['AvailabilityZone'] for s in subnets}
        nat_per_az = defaultdict(int)
        for ng in nat_gws:
            az = subnet_az.get(ng.get('SubnetId'), 'unknown')
            nat_per_az[az] += 1
        if nat_per_az:
            max_az = max(nat_per_az, key=nat_per_az.get)
            max_usage = nat_per_az[max_az]
        else:
            max_az, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-FE5A380F',
            quota_name='NAT gateways per Availability Zone',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='AvailabilityZone', max_resource_id=max_az,
            data_source='ec2:DescribeNatGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-FE5A380F failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  PER-RESOURCE CHECKS  (report resource with highest usage)
    # ══════════════════════════════════════════════════════════════════

    # L-0EA8095F  Inbound or outbound rules per security group
    try:
        limit = get_limit('L-0EA8095F')
        sg_rules = {}
        for sg in sgs:
            total_rules = (len(sg.get('IpPermissions', []))
                           + len(sg.get('IpPermissionsEgress', [])))
            sg_rules[sg['GroupId']] = total_rules
        if sg_rules:
            max_id = max(sg_rules, key=sg_rules.get)
            max_usage = sg_rules[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-0EA8095F',
            quota_name='Inbound or outbound rules per security group',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='SecurityGroup', max_resource_id=max_id,
            data_source='ec2:DescribeSecurityGroups'))
    except Exception as e:
        logger.warning(f"VPC check L-0EA8095F failed: {e}")

    # L-93826ACB  Routes per route table
    try:
        limit = get_limit('L-93826ACB')
        rt_routes = {rt['RouteTableId']: len(rt.get('Routes', [])) for rt in rts}
        if rt_routes:
            max_id = max(rt_routes, key=rt_routes.get)
            max_usage = rt_routes[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-93826ACB', quota_name='Routes per route table',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='RouteTable', max_resource_id=max_id,
            data_source='ec2:DescribeRouteTables'))
    except Exception as e:
        logger.warning(f"VPC check L-93826ACB failed: {e}")

    # L-2AEEBF1A  Rules per network ACL
    try:
        limit = get_limit('L-2AEEBF1A')
        nacl_rules = {n['NetworkAclId']: len(n.get('Entries', [])) for n in nacls}
        if nacl_rules:
            max_id = max(nacl_rules, key=nacl_rules.get)
            max_usage = nacl_rules[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-2AEEBF1A', quota_name='Rules per network ACL',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='NetworkAcl', max_resource_id=max_id,
            data_source='ec2:DescribeNetworkAcls'))
    except Exception as e:
        logger.warning(f"VPC check L-2AEEBF1A failed: {e}")

    # L-2AFB9258  Security groups per network interface
    try:
        limit = get_limit('L-2AFB9258')
        eni_sgs = {e['NetworkInterfaceId']: len(e.get('Groups', []))
                   for e in enis}
        if eni_sgs:
            max_id = max(eni_sgs, key=eni_sgs.get)
            max_usage = eni_sgs[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-2AFB9258',
            quota_name='Security groups per network interface',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='NetworkInterface', max_resource_id=max_id,
            data_source='ec2:DescribeNetworkInterfaces'))
    except Exception as e:
        logger.warning(f"VPC check L-2AFB9258 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  PER-NAT-GATEWAY CHECKS  (report NAT GW with highest usage)
    # ══════════════════════════════════════════════════════════════════

    # L-5F53652F  Elastic IP address quota per NAT gateway
    try:
        limit = get_limit('L-5F53652F')
        nat_eips = {}
        for ng in nat_gws:
            ng_id = ng['NatGatewayId']
            eip_count = sum(1 for addr in ng.get('NatGatewayAddresses', [])
                           if addr.get('AllocationId'))
            nat_eips[ng_id] = eip_count
        if nat_eips:
            max_id = max(nat_eips, key=nat_eips.get)
            max_usage = nat_eips[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-5F53652F',
            quota_name='Elastic IP address quota per NAT gateway',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='NatGateway', max_resource_id=max_id,
            data_source='ec2:DescribeNatGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-5F53652F failed: {e}")

    # L-DFA99DE7  Private IP address quota per NAT gateway
    try:
        limit = get_limit('L-DFA99DE7')
        nat_private_ips = {}
        for ng in nat_gws:
            ng_id = ng['NatGatewayId']
            private_ip_count = sum(1 for addr in ng.get('NatGatewayAddresses', [])
                                  if addr.get('PrivateIp'))
            nat_private_ips[ng_id] = private_ip_count
        if nat_private_ips:
            max_id = max(nat_private_ips, key=nat_private_ips.get)
            max_usage = nat_private_ips[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-DFA99DE7',
            quota_name='Private IP address quota per NAT gateway',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='NatGateway', max_resource_id=max_id,
            data_source='ec2:DescribeNatGateways'))
    except Exception as e:
        logger.warning(f"VPC check L-DFA99DE7 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  NETWORK ADDRESS USAGE CHECKS  (per VPC, via CloudWatch AWS/EC2)
    # ══════════════════════════════════════════════════════════════════
    #  These quotas have NO UsageMetric in Service Quotas, but AWS publishes
    #  per-VPC metrics in the AWS/EC2 namespace when a VPC exists:
    #    NetworkAddressUsage          → L-BB24F6E5
    #    NetworkAddressUsagePeered    → L-CD17FD4B
    #  See: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cloudwatch.html#nau-cloudwatch
    #  If no VPC exists (or metric not yet published), usage defaults to 0.

    cw = session.client('cloudwatch')
    cw_end = datetime.now(timezone.utc)
    cw_start = cw_end - timedelta(hours=1)
    vpc_ids = [v['VpcId'] for v in vpcs]

    def _get_nau_per_vpc(metric_name):
        """Query a per-VPC NAU metric from AWS/EC2 and return {vpc_id: max_value}."""
        nau_map = {}
        if not vpc_ids:
            return nau_map
        # Build one MetricDataQuery per VPC
        queries = []
        id_to_vpc = {}
        for i, vid in enumerate(vpc_ids):
            qid = f"m{i}"
            queries.append({
                'Id': qid,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': metric_name,
                        'Dimensions': [{'Name': 'VpcId', 'Value': vid}]
                    },
                    'Period': 3600,
                    'Stat': 'Maximum'
                },
                'ReturnData': True
            })
            id_to_vpc[qid] = vid
        # CloudWatch allows max 500 queries per call
        for batch_start in range(0, len(queries), 500):
            batch = queries[batch_start:batch_start + 500]
            try:
                next_token = None
                while True:
                    kwargs = {
                        'MetricDataQueries': batch,
                        'StartTime': cw_start,
                        'EndTime': cw_end
                    }
                    if next_token:
                        kwargs['NextToken'] = next_token
                    resp = cw.get_metric_data(**kwargs)
                    for result in resp.get('MetricDataResults', []):
                        values = result.get('Values', [])
                        if values:
                            nau_map[id_to_vpc[result['Id']]] = int(max(values))
                    next_token = resp.get('NextToken')
                    if not next_token:
                        break
            except Exception as e:
                logger.warning(f"CloudWatch {metric_name} batch query failed: {e}")
        return nau_map

    # L-BB24F6E5  Network Address Usage (per VPC)
    try:
        limit = get_limit('L-BB24F6E5')
        nau_per_vpc = _get_nau_per_vpc('NetworkAddressUsage')
        if nau_per_vpc:
            max_id = max(nau_per_vpc, key=nau_per_vpc.get)
            max_usage = nau_per_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-BB24F6E5', quota_name='Network Address Usage',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='CLOUDWATCH_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='cloudwatch:AWS/EC2:NetworkAddressUsage'))
    except Exception as e:
        logger.warning(f"VPC check L-BB24F6E5 failed: {e}")

    # L-CD17FD4B  Peered Network Address Usage (per VPC)
    try:
        limit = get_limit('L-CD17FD4B')
        peered_nau_per_vpc = _get_nau_per_vpc('NetworkAddressUsagePeered')
        if peered_nau_per_vpc:
            max_id = max(peered_nau_per_vpc, key=peered_nau_per_vpc.get)
            max_usage = peered_nau_per_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-CD17FD4B', quota_name='Peered Network Address Usage',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='CLOUDWATCH_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='cloudwatch:AWS/EC2:NetworkAddressUsagePeered'))
    except Exception as e:
        logger.warning(f"VPC check L-CD17FD4B failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  RAM-BASED CHECKS  (VPC sharing)
    # ══════════════════════════════════════════════════════════════════

    # L-2C462E13  Participant accounts per VPC
    #  Count unique external accounts with which each VPC's subnets are shared.
    try:
        ram = session.client('ram')
        limit = get_limit('L-2C462E13')

        # Map subnets → VPC
        subnet_to_vpc = {s['SubnetId']: s['VpcId'] for s in subnets}

        # Find shared subnet resources via RAM
        shared_resources = []
        paginator = ram.get_paginator('list_resources')
        for page in paginator.paginate(resourceOwner='SELF',
                                       resourceType='ec2:Subnet'):
            shared_resources.extend(page.get('resources', []))

        # For each shared subnet find associated principals (accounts)
        vpc_participants = defaultdict(set)
        for res in shared_resources:
            res_arn = res.get('arn', '')
            share_arn = res.get('resourceShareArn')
            # Extract subnet ID from ARN: arn:aws:ec2:region:account:subnet/subnet-xxx
            subnet_id = res_arn.split('/')[-1] if '/subnet-' in res_arn else None
            vpc_id = subnet_to_vpc.get(subnet_id)
            if vpc_id and share_arn:
                # Get principals for this resource share
                try:
                    assoc_paginator = ram.get_paginator('list_principals')
                    for assoc_page in assoc_paginator.paginate(
                            resourceOwner='SELF',
                            resourceShareArns=[share_arn]):
                        for principal in assoc_page.get('principals', []):
                            pid = principal.get('id', '')
                            # Only count AWS account IDs (12 digits)
                            if len(pid) == 12 and pid.isdigit():
                                vpc_participants[vpc_id].add(pid)
                except Exception:
                    pass

        participants_per_vpc = {vpc_id: len(accts)
                                for vpc_id, accts in vpc_participants.items()}
        if participants_per_vpc:
            max_id = max(participants_per_vpc, key=participants_per_vpc.get)
            max_usage = participants_per_vpc[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-2C462E13', quota_name='Participant accounts per VPC',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='VPC', max_resource_id=max_id,
            data_source='ram:ListResources+ListPrincipals'))
    except Exception as e:
        logger.warning(f"VPC check L-2C462E13 failed: {e}")

    # L-44499CD2  Subnets that can be shared with an account
    #  From participant perspective: count subnets shared with this account via RAM.
    try:
        limit = get_limit('L-44499CD2')
        shared_with_me = []
        paginator = ram.get_paginator('list_resources')
        for page in paginator.paginate(resourceOwner='OTHER-ACCOUNTS',
                                       resourceType='ec2:Subnet'):
            shared_with_me.extend(page.get('resources', []))
        vpc_quotas.append(entry(
            quota_code='L-44499CD2',
            quota_name='Subnets that can be shared with an account',
            limit_value=limit, usage_value=len(shared_with_me),
            collector_type='ACCOUNT_TOTAL', calculation_method='ACCOUNT_TOTAL',
            data_source='ram:ListResources'))
    except Exception as e:
        logger.warning(f"VPC check L-44499CD2 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  ADDITIONAL CHECKS
    # ══════════════════════════════════════════════════════════════════

    # L-A272D574  VPC associations per security group
    #  Count distinct VPCs referencing each SG (via peering SG rules).
    try:
        limit = get_limit('L-A272D574')
        sg_vpc_refs = defaultdict(set)
        for sg in sgs:
            sg_id = sg['GroupId']
            sg_vpc = sg.get('VpcId')
            # The SG's own VPC always counts
            if sg_vpc:
                sg_vpc_refs[sg_id].add(sg_vpc)
            # Check inbound rules for cross-VPC SG references
            for perm in sg.get('IpPermissions', []):
                for pair in perm.get('UserIdGroupPairs', []):
                    ref_vpc = pair.get('VpcId')
                    if ref_vpc:
                        # This SG is referenced from ref_vpc
                        ref_sg = pair.get('GroupId')
                        if ref_sg:
                            sg_vpc_refs[ref_sg].add(sg_vpc)
            for perm in sg.get('IpPermissionsEgress', []):
                for pair in perm.get('UserIdGroupPairs', []):
                    ref_vpc = pair.get('VpcId')
                    if ref_vpc:
                        ref_sg = pair.get('GroupId')
                        if ref_sg:
                            sg_vpc_refs[ref_sg].add(sg_vpc)
        assoc_counts = {sg_id: len(vpcs_set)
                        for sg_id, vpcs_set in sg_vpc_refs.items()}
        if assoc_counts:
            max_id = max(assoc_counts, key=assoc_counts.get)
            max_usage = assoc_counts[max_id]
        else:
            max_id, max_usage = None, 0
        vpc_quotas.append(entry(
            quota_code='L-A272D574',
            quota_name='VPC associations per security group',
            limit_value=limit, usage_value=max_usage,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='SecurityGroup', max_resource_id=max_id,
            data_source='ec2:DescribeSecurityGroups'))
    except Exception as e:
        logger.warning(f"VPC check L-A272D574 failed: {e}")

    # L-42B9C2CA  VPC Block Public Access exclusions per account per Region
    try:
        limit = get_limit('L-42B9C2CA')
        exclusions = []
        try:
            resp = ec2.describe_vpc_block_public_access_exclusions()
            exclusions = resp.get('VpcBlockPublicAccessExclusions', [])
        except AttributeError:
            # API not available in this boto3 version
            pass
        vpc_quotas.append(entry(
            quota_code='L-42B9C2CA',
            quota_name='VPC Block Public Access exclusions per account per Region',
            limit_value=limit, usage_value=len(exclusions),
            data_source='ec2:DescribeVpcBlockPublicAccessExclusions'))
    except Exception as e:
        logger.warning(f"VPC check L-42B9C2CA failed: {e}")

    # L-8312C5BB  VPC peering connection request expiry hours
    #  Static configuration value, not a usage-based quota – skipped.

    logger.info(f"VPC collector: completed with {len(vpc_quotas)} quota entries")
    return vpc_quotas
