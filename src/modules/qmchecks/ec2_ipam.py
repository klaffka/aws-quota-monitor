"""Amazon VPC IP Address Manager resource quotas.

The four contiguous-block quotas (`Max IPv4/IPv6 Contig Block Size` and
`Max IPv4/IPv6 Contig Blocks`) describe what an allocation request may ask for
rather than an inventory, so they are not measured here.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

EC2 = 'ec2'


def _identity(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'IPAM {subject} is missing its identity')
    return value


def _count(item, field, subject):
    value = item.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise NoData(f'IPAM {subject} has no {field}')
    return value


def ipams(ctx):
    return {_identity(item, 'IpamId', 'instance'): item
            for item in ctx.call(EC2, 'describe_ipams', 'Ipams')}


def pools(ctx):
    return {_identity(item, 'IpamPoolId', 'pool'): item
            for item in ctx.call(EC2, 'describe_ipam_pools', 'IpamPools')}


def _reported_count(inventory, field, subject, resource_type, source):
    """Report the largest count AWS already keeps on the resource itself."""
    def check(ctx):
        values = [(identity, _count(item, field, subject), None)
                  for identity, item in inventory(ctx).items()]
        return maximum(values, resource_type, source)
    return check


def scopes_per_ipam(ctx):
    return _reported_count(ipams, 'ScopeCount', 'instance', 'IPAM',
                           'ec2:DescribeIpams')(ctx)


def associations_per_ipam(ctx):
    return _reported_count(ipams, 'ResourceDiscoveryAssociationCount', 'instance',
                           'IPAM', 'ec2:DescribeIpams')(ctx)


def pools_per_scope(ctx):
    values = [(_identity(item, 'IpamScopeId', 'scope'),
               _count(item, 'PoolCount', 'scope'), None)
              for item in ctx.call(EC2, 'describe_ipam_scopes', 'IpamScopes')]
    return maximum(values, 'IPAMScope', 'ec2:DescribeIpamScopes')


def pool_depth(ctx):
    values = [(identity, _count(pool, 'PoolDepth', 'pool'), None)
              for identity, pool in pools(ctx).items()]
    return maximum(values, 'IPAMPool', 'ec2:DescribeIpamPools')


def cidrs_per_pool(ctx):
    values = []
    for identity in pools(ctx):
        cidrs = ctx.call(EC2, 'get_ipam_pool_cidrs', 'IpamPoolCidrs',
                         IpamPoolId=identity)
        for cidr in cidrs:
            if not isinstance(cidr.get('Cidr'), str):
                raise NoData('IPAM pool CIDR is missing its range')
        values.append((identity, len(cidrs), None))
    return maximum(values, 'IPAMPool', 'ec2:GetIpamPoolCidrs')


def resource_discoveries(ctx):
    return {_identity(item, 'IpamResourceDiscoveryId', 'resource discovery'): item
            for item in ctx.call(EC2, 'describe_ipam_resource_discoveries',
                                 'IpamResourceDiscoveries')}


def organizational_unit_exclusions(ctx):
    values = []
    for identity, item in resource_discoveries(ctx).items():
        exclusions = item.get('OrganizationalUnitExclusions') or []
        if not isinstance(exclusions, list):
            raise NoData('IPAM resource discovery has an invalid exclusion list')
        values.append((identity, len(exclusions), None))
    return maximum(values, 'IPAMResourceDiscovery',
                   'ec2:DescribeIpamResourceDiscoveries')


def _children_per_ipam(ctx, method, key, parent_field, subject, source):
    """Count child resources per parent IPAM, including IPAMs with none."""
    counts = Counter({identity: 0 for identity in ipams(ctx)})
    for item in ctx.call(EC2, method, key):
        parent = item.get(parent_field)
        if not isinstance(parent, str) or not parent:
            raise NoData(f'IPAM {subject} has no parent')
        counts[parent] += 1
    return maximum(((parent, count, None) for parent, count in counts.items()),
                   'IPAM', source)


def internet_registry_associations_per_ipam(ctx):
    return _children_per_ipam(
        ctx, 'describe_ipam_internet_registry_associations',
        'IpamInternetRegistryAssociations', 'IpamId', 'internet registry association',
        'ec2:DescribeIpamInternetRegistryAssociations')


def prefix_list_resolvers_per_ipam(ctx):
    # Resolvers reference their IPAM by ARN rather than by ID.
    arns = {item.get('IpamArn'): identity for identity, item in ipams(ctx).items()}
    counts = Counter({identity: 0 for identity in ipams(ctx)})
    for item in ctx.call(EC2, 'describe_ipam_prefix_list_resolvers',
                         'IpamPrefixListResolvers'):
        parent = arns.get(item.get('IpamArn'))
        if parent is None:
            raise NoData('IPAM prefix list resolver has an unknown parent')
        counts[parent] += 1
    return maximum(((parent, count, None) for parent, count in counts.items()),
                   'IPAM', 'ec2:DescribeIpamPrefixListResolvers')


CHECKS = [
    ('L-F8B4A9E6', 'IPAMs per Region',
     lambda ctx: dict(usage=len(ipams(ctx)), source='ec2:DescribeIpams',
                      method='ACCOUNT_COUNT')),
    ('L-F0D8E837', 'Resource discoveries per Region',
     lambda ctx: dict(usage=len(resource_discoveries(ctx)),
                      source='ec2:DescribeIpamResourceDiscoveries',
                      method='ACCOUNT_COUNT')),
    ('L-F493CFD2', 'Scopes per IPAM', scopes_per_ipam),
    ('L-037D1B6C', 'Resource discovery associations per IPAM', associations_per_ipam),
    ('L-7319AFC3', 'Pools per IPAM scope', pools_per_scope),
    ('L-047C0565', 'IPAM pool depth', pool_depth),
    ('L-0BC051D6', 'CIDRs per IPAM pool', cidrs_per_pool),
    ('L-CD416D24', 'Organizational unit exclusions per resource discovery',
     organizational_unit_exclusions),
    ('L-BB69F419', 'Internet Registry Associations per IPAM',
     internet_registry_associations_per_ipam),
    ('L-853116AC', 'Prefix List Resolvers per IPAM', prefix_list_resolvers_per_ipam),
]


def get_current_quotastatus_ec2_ipam(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ec2-ipam' for service, _ in context.quotas):
        return []
    return context.run('ec2-ipam', CHECKS, skip)
