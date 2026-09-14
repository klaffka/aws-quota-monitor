import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ec2_ipam
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

IPAM = 'ipam-00000000000000001'
OTHER = 'ipam-00000000000000002'
ARN = f'arn:aws:ec2::123456789012:ipam/{IPAM}'
OTHER_ARN = f'arn:aws:ec2::123456789012:ipam/{OTHER}'
POOL = 'ipam-pool-00000000000000001'
SCOPE = 'ipam-scope-00000000000000001'
DISCOVERY = 'ipam-res-disco-00000000000000001'


def context(code='L-F8B4A9E6'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ec2-ipam', 'QuotaCode': code, 'Value': 50}],
                        account='123456789012')


def ipam(identity=IPAM, arn=ARN, scopes=2, associations=1):
    return {'IpamId': identity, 'IpamArn': arn, 'ScopeCount': scopes,
            'ResourceDiscoveryAssociationCount': associations, 'State': 'create-complete'}


def check(code):
    return next(fn for quota, _, fn in ec2_ipam.CHECKS if quota == code)


def test_counts_that_aws_reports_on_the_resource_are_used_directly():
    for code, field, expected in (('L-F493CFD2', 'ScopeCount', 5),
                                  ('L-037D1B6C', 'ResourceDiscoveryAssociationCount', 5)):
        ctx = context(code)
        with Stubber(ctx.client('ec2')) as stub:
            stub.add_response('describe_ipams', {'Ipams': [
                ipam(), dict(ipam(OTHER, OTHER_ARN), **{field: 5})]}, {})
            result = check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected, OTHER), code
            stub.assert_no_pending_responses()


def test_a_missing_reported_count_raises_nodata():
    ctx = context('L-F493CFD2')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipams', {'Ipams': [
            {'IpamId': IPAM, 'IpamArn': ARN, 'State': 'create-complete'}]}, {})
        with pytest.raises(NoData, match='ScopeCount'):
            check('L-F493CFD2')(ctx)


def test_pools_per_scope_uses_the_scope_inventory():
    ctx = context('L-7319AFC3')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipam_scopes', {'IpamScopes': [
            {'IpamScopeId': SCOPE, 'PoolCount': 3},
            {'IpamScopeId': 'ipam-scope-00000000000000002', 'PoolCount': 1}]}, {})
        result = check('L-7319AFC3')(ctx)
        assert (result['usage'], result['resource_id']) == (3, SCOPE)
        stub.assert_no_pending_responses()


def test_cidrs_are_counted_per_pool():
    ctx = context('L-0BC051D6')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipam_pools', {'IpamPools': [
            {'IpamPoolId': POOL, 'PoolDepth': 1}]}, {})
        stub.add_response('get_ipam_pool_cidrs', {'IpamPoolCidrs': [
            {'Cidr': '10.0.0.0/16', 'State': 'provisioned'},
            {'Cidr': '10.1.0.0/16', 'State': 'provisioned'}]}, {'IpamPoolId': POOL})
        result = check('L-0BC051D6')(ctx)
        assert (result['usage'], result['resource_id']) == (2, POOL)
        stub.assert_no_pending_responses()


def test_organizational_unit_exclusions_default_to_zero():
    ctx = context('L-CD416D24')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipam_resource_discoveries', {
            'IpamResourceDiscoveries': [
                {'IpamResourceDiscoveryId': DISCOVERY},
                {'IpamResourceDiscoveryId': 'ipam-res-disco-00000000000000002',
                 'OrganizationalUnitExclusions': [
                     {'OrganizationsEntityPath': 'o-1/r-1/ou-1'},
                     {'OrganizationsEntityPath': 'o-1/r-1/ou-2'}]}]}, {})
        assert check('L-CD416D24')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_internet_registry_associations_count_per_parent_ipam():
    ctx = context('L-BB69F419')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipams', {'Ipams': [ipam(), ipam(OTHER, OTHER_ARN)]}, {})
        stub.add_response('describe_ipam_internet_registry_associations', {
            'IpamInternetRegistryAssociations': [
                {'IpamInternetRegistryAssociationId': 'ipam-ira-1', 'IpamId': IPAM},
                {'IpamInternetRegistryAssociationId': 'ipam-ira-2', 'IpamId': IPAM}]}, {})
        result = check('L-BB69F419')(ctx)
        assert (result['usage'], result['resource_id']) == (2, IPAM)
        stub.assert_no_pending_responses()


def test_prefix_list_resolvers_are_matched_by_ipam_arn():
    ctx = context('L-853116AC')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipams', {'Ipams': [ipam(), ipam(OTHER, OTHER_ARN)]}, {})
        stub.add_response('describe_ipam_prefix_list_resolvers', {
            'IpamPrefixListResolvers': [
                {'IpamPrefixListResolverId': 'ipam-plr-1', 'IpamArn': OTHER_ARN}]}, {})
        result = check('L-853116AC')(ctx)
        assert (result['usage'], result['resource_id']) == (1, OTHER)
        stub.assert_no_pending_responses()


def test_a_resolver_of_an_unknown_ipam_raises_nodata():
    ctx = context('L-853116AC')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipams', {'Ipams': [ipam()]}, {})
        stub.add_response('describe_ipam_prefix_list_resolvers', {
            'IpamPrefixListResolvers': [
                {'IpamPrefixListResolverId': 'ipam-plr-1',
                 'IpamArn': 'arn:aws:ec2::123456789012:ipam/ipam-0000000000000dead'}]}, {})
        with pytest.raises(NoData, match='unknown parent'):
            check('L-853116AC')(ctx)


def test_region_counts_report_the_inventory_size():
    ctx = context('L-F8B4A9E6')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_ipams', {'Ipams': [ipam(), ipam(OTHER, OTHER_ARN)]}, {})
        assert check('L-F8B4A9E6')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_every_ipam_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'ec2-ipam'}
    assert {code for code, _, _ in ec2_ipam.CHECKS} <= registered
