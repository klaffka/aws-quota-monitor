from datetime import datetime, UTC
from unittest.mock import Mock
import boto3
import pytest
from botocore.stub import Stubber
from modules.qmcore.aws import CheckContext, paginate, Unsupported
from modules.qmcore.model import measurement, valid_measurement
from modules.qmchecks.ec2.ec2 import (ami_sharing, vpn_rules, capacity_blocks, ami_count,
                                      public_ami_count, launch_template_versions,
                                      vpn_connections_per_vgw)
from modules.qmchecks.vpc.vpc import security_group_rules, acl_rules, route_rules, nat_per_az, nat_per_vpc, sg_associations, participants
from modules.qmchecks.lambda_checks.lambda_checks import (
    environment_size, storage, policy_size, direct_upload_package_size,
)

NOW = datetime(2026, 3, 1, tzinfo=UTC)


@pytest.mark.parametrize('limit,usage,status,pct', [(10, 8, 'OK', 80), (0, 8, 'NO_DATA', None),
    (None, 8, 'NO_DATA', None), (10, None, 'NO_DATA', None), (-1, 8, 'NO_DATA', None),
    (10, float('nan'), 'NO_DATA', None), (float('inf'), 8, 'NO_DATA', None), (10, 0, 'OK', 0)])
def test_validation(limit, usage, status, pct):
    entry = measurement('a', 'r', 'ec2', 'q', 'quota', limit, usage, now=NOW)
    assert entry['qualityStatus'] == status
    assert entry['utilizationPct'] == pct
    assert valid_measurement(entry) == (status == 'OK')


def test_real_sdk_pagination_and_partial_inventory():
    client = boto3.client('ec2', region_name='eu-central-1')
    with Stubber(client) as stub:
        stub.add_response('describe_images', {'Images': [{'ImageId': 'ami-1'}], 'NextToken': 'next'}, {'Owners': ['self']})
        stub.add_response('describe_images', {'Images': [{'ImageId': 'ami-2'}]}, {'Owners': ['self'], 'NextToken': 'next'})
        assert len(paginate(client, 'describe_images', 'Images', Owners=['self'])) == 2
        stub.assert_no_pending_responses()
    with Stubber(client) as stub:
        stub.add_response('describe_images', {'Images': [{'ImageId': 'ami-1'}], 'NextToken': 'next'}, {'Owners': ['self']})
        stub.add_client_error('describe_images', service_error_code='UnauthorizedOperation',
                              expected_params={'Owners': ['self'], 'NextToken': 'next'})
        with pytest.raises(Exception, match='UnauthorizedOperation'):
            paginate(client, 'describe_images', 'Images', Owners=['self'])


def test_ami_is_raw_entity_count_excludes_public():
    ctx = Mock()
    ctx.call.side_effect = [[{'ImageId': 'ami-1'}, {'ImageId': 'ami-2'}],
        {'LaunchPermissions': [{'UserId': '1'}, {'UserId': '2'}, {'OrganizationArn': 'org'}, {'Group': 'all'}]},
        {'LaunchPermissions': [{'UserId': '1'}]}]
    result = ami_sharing(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'ami-1')


def test_ami_counts_are_owner_scoped_and_public_is_permission_based():
    ctx = Mock(account='123456789012')
    ctx.call.side_effect = [
        [{'ImageId': 'ami-1'}, {'ImageId': 'ami-2'}],
        [{'ImageId': 'ami-1'}, {'ImageId': 'ami-2'}],
        [{'ImageId': 'ami-1'}, {'ImageId': 'ami-2'}],
        {'LaunchPermissions': [{'Group': 'all'}]},
        {'LaunchPermissions': [{'UserId': '123456789012'}]},
    ]
    assert ami_count(ctx)['usage'] == 2
    assert public_ami_count(ctx)['usage'] == 1
    assert ctx.call.call_args_list[0].kwargs == {'Owners': ['self']}


def test_launch_template_versions_use_maximum_per_template():
    ctx = Mock(account='123456789012')
    ctx.call.side_effect = [
        [{'LaunchTemplateId': 'lt-1'}, {'LaunchTemplateId': 'lt-2'}],
        [{'VersionNumber': 1}, {'VersionNumber': 2}],
        [{'VersionNumber': 1}],
    ]
    result = launch_template_versions(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'lt-1')


def test_vpn_max_per_endpoint():
    ctx = Mock()
    ctx.call.side_effect = [[{'ClientVpnEndpointId': 'vpn-1'}, {'ClientVpnEndpointId': 'vpn-2'}], [{}]*8, [{}]*3]
    result = vpn_rules(ctx)
    assert (result['usage'], result['resource_id']) == (8, 'vpn-1')


def test_site_to_site_vpn_connections_per_gateway():
    ctx = Mock()
    ctx.call.return_value = [
        {'VpnConnectionId': 'v1', 'VpnGatewayId': 'vgw-1'},
        {'VpnConnectionId': 'v2', 'VpnGatewayId': 'vgw-1'},
        {'VpnConnectionId': 'v3', 'VpnGatewayId': 'vgw-2'},
    ]
    result = vpn_connections_per_vgw(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'vgw-1')


def test_capacity_reservations_count_blocks_not_instances():
    ctx = Mock(account='a', now=NOW)
    base = dict(ReservationType='capacity-block', State='active', InstanceType='p4d.24xlarge', OwnerId='a',
                TotalInstanceCount=64, CapacityBlockId='block-1', CapacityReservationId='cr-1')
    ctx.call.return_value = [base, dict(base, CapacityReservationId='cr-2'), dict(base, State='scheduled', CapacityBlockId='future'),
        dict(base, OwnerId='other', CapacityBlockId='shared'), dict(base, ReservationType='default', CapacityBlockId='ordinary')]
    # The quota names a family, so every size of p4d counts against it.
    assert capacity_blocks(ctx, 'p4d')['usage'] == 1
    assert capacity_blocks(ctx, 'p5')['usage'] == 0


def test_sg_direction_family_and_prefix_weight():
    ctx = Mock()
    sg = {'GroupId': 'sg-1', 'IpPermissions': [{'IpRanges': [{}]*2, 'Ipv6Ranges': [{}]*4,
            'UserIdGroupPairs': [{}], 'PrefixListIds': [{'PrefixListId': 'pl-custom'}]}],
          'IpPermissionsEgress': [{'IpRanges': [{}]*8}]}
    ctx.call.side_effect = [[sg], [{'PrefixListId': 'pl-custom', 'OwnerId': 'account', 'AddressFamily': 'ipv4', 'MaxEntries': 20}]]
    result = security_group_rules(ctx)
    assert result['usage'] == 23
    assert result['meta'] == {'direction': 'inbound', 'addressFamily': 'ipv4'}


def test_routes_family_propagation_and_aws_prefix_weight():
    ctx = Mock()
    ctx.call.side_effect = [[{'RouteTableId': 'rt-1', 'Routes': [
        {'DestinationCidrBlock': '0.0.0.0/0'}, {'DestinationIpv6CidrBlock': '::/0'},
        {'DestinationCidrBlock': '10.0.0.0/16', 'Origin': 'EnableVgwRoutePropagation'},
        {'DestinationPrefixListId': 'pl-cf'}]}],
        [{'OwnerId': 'AWS', 'AddressFamily': 'ipv4', 'PrefixListName': 'com.amazonaws.global.cloudfront.origin-facing'}]]
    assert route_rules(ctx)['usage'] == 56


def test_acl_direction_excludes_default_deny():
    ctx = Mock()
    ctx.call.return_value = [{'NetworkAclId': 'acl-1', 'Entries': [
        {'RuleNumber': 100, 'Egress': False}, {'RuleNumber': 101, 'Egress': False},
        {'RuleNumber': 100, 'Egress': True}, {'RuleNumber': 32767, 'Egress': False}, {'RuleNumber': 32767, 'Egress': True}]}]
    assert acl_rules(ctx)['usage'] == 2


def test_inventory_error_is_cached_and_checks_are_isolated():
    session = Mock(region_name='eu-central-1')
    ctx = CheckContext(session, account='a', now=NOW, quotas=[
        {'ServiceCode': 'ec2', 'QuotaCode': 'good', 'Value': 10}, {'ServiceCode': 'ec2', 'QuotaCode': 'bad', 'Value': 10}])
    def fail(c):
        raise RuntimeError('Throttling')
    results = ctx.run('ec2', [('bad', 'bad', fail), ('good', 'good', lambda c: {'usage': 8})])
    assert [r['qualityStatus'] for r in results] == ['ERROR', 'OK']
    assert results[1]['utilizationPct'] == 80
    session.client.return_value.can_paginate.return_value = False
    session.client.return_value.describe_vpcs.side_effect = RuntimeError('AccessDenied')
    for _ in range(2):
        with pytest.raises(RuntimeError):
            ctx.call('ec2', 'describe_vpcs', 'Vpcs')
    assert session.client.return_value.describe_vpcs.call_count == 1


def test_lambda_utf8_and_precise_storage():
    assert environment_size({'Environment': {'Variables': {'x': 'ä😀'}}}) == 7
    with pytest.raises(RuntimeError):
        environment_size({'Environment': {'Error': {'ErrorCode': 'AccessDenied'}}})
    ctx = Mock()
    ctx.call.return_value = {'AccountUsage': {'TotalCodeSize': 1}, 'AccountLimit': {'TotalCodeSize': 1024**3}}
    assert storage(ctx) == dict(usage=1, limit=1024**3, unit='Bytes', source='lambda:GetAccountSettings', method='ACCOUNT_TOTAL')


def test_sg_associations_use_association_api():
    ctx = Mock()
    ctx.call.return_value = [{'GroupId': 'sg-1', 'VpcId': 'vpc-2', 'State': 'associated'},
                             {'GroupId': 'sg-1', 'VpcId': 'vpc-3', 'State': 'associated'},
                             {'GroupId': 'sg-1', 'VpcId': 'vpc-4', 'State': 'disassociated'}]
    assert sg_associations(ctx)['usage'] == 2
    assert ctx.call.call_args.args[1] == 'describe_security_group_vpc_associations'


def test_nau_missing_resource_invalidates_complete_maximum():
    from modules.qmchecks.vpc.vpc import nau
    from modules.qmcore.aws import NoData
    ctx = Mock(now=NOW, account='a', region='eu-central-1')
    ctx.call.return_value = [{'VpcId': 'vpc-1'}, {'VpcId': 'vpc-2'}]
    ctx.client.return_value.get_metric_data.return_value = {'MetricDataResults': [
        {'Id': 'm0', 'StatusCode': 'Complete', 'Values': [10], 'Timestamps': [NOW.replace(minute=0)]},
        {'Id': 'm1', 'StatusCode': 'Complete', 'Values': [], 'Timestamps': []}]}
    with pytest.raises(NoData):
        nau(ctx, 'NetworkAddressUsage')


def test_nat_pending_and_deleting_count_per_az():
    ctx = Mock()
    ctx.call.side_effect = [[{'SubnetId': 's1', 'AvailabilityZone': 'az1'}, {'SubnetId': 's2', 'AvailabilityZone': 'az2'}],
        [{'NatGatewayId': 'n1', 'SubnetId': 's1', 'State': 'available'},
         {'NatGatewayId': 'n2', 'SubnetId': 's1', 'State': 'pending'},
         {'NatGatewayId': 'n3', 'SubnetId': 's1', 'State': 'deleting'},
         {'NatGatewayId': 'n4', 'SubnetId': 's2', 'State': 'available'},
         {'NatGatewayId': 'n5', 'SubnetId': 's1', 'State': 'deleted'}]]
    assert nat_per_az(ctx)['usage'] == 3


def test_prefix_list_unknown_weight_is_unsupported():
    from modules.qmchecks.vpc.vpc import prefix_info
    ctx = Mock()
    ctx.call.return_value = [{'OwnerId': 'AWS', 'AddressFamily': 'ipv4', 'PrefixListName': 'com.amazonaws.region.new-service'}]
    with pytest.raises(Unsupported):
        prefix_info(ctx, 'pl-unknown')


def test_no_policy_validates_resource_still_exists_and_permissions_propagate():
    from botocore.exceptions import ClientError
    ctx = Mock()
    no_policy = ClientError({'Error': {'Code': 'ResourceNotFoundException', 'Message': 'not found'}}, 'GetPolicy')
    ctx.call.side_effect = [no_policy, {'FunctionName': 'fn'}]
    assert policy_size(ctx, {'FunctionArn': 'arn:fn'}) == 0
    assert ctx.call.call_args.args[1] == 'get_function_configuration'
    ctx.call.side_effect = ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'denied'}}, 'GetPolicy')
    with pytest.raises(ClientError):
        policy_size(ctx, {'FunctionArn': 'arn:fn'})


def test_lambda_alias_policy_included():
    from modules.qmchecks.lambda_checks.lambda_checks import policies
    ctx = Mock()
    ctx.quotas = {('lambda', 'L-07A00131'): {'Unit': 'Kilobytes', 'Value': 20}}
    ctx.call.side_effect = [[{'FunctionName': 'fn', 'FunctionArn': 'arn:fn', 'Version': '$LATEST'}],
                           [{'AliasArn': 'arn:fn:prod'}], {'Policy': '{}'}, {'Policy': '{"example":true}'}]
    result = policies(ctx)
    assert result['resource_id'] == 'arn:fn:prod'
    assert result['usage'] == len('{"example":true}')
    assert result['limit'] == 20480


def test_kafka_default_mode_includes_msk_and_self_managed():
    from modules.qmchecks.lambda_checks.lambda_checks import kafka_default_mode
    ctx = Mock()
    ctx.call.return_value = [
        {'AmazonManagedKafkaEventSourceConfig': {'ConsumerGroupId': 'a'}},
        {'AmazonManagedKafkaEventSourceConfig': {'ConsumerGroupId': 'b'}, 'ProvisionedPollerConfig': {'MinimumPollers': 1}},
        {'SelfManagedKafkaEventSourceConfig': {'ConsumerGroupId': 'c'}},
        {'SelfManagedKafkaEventSourceConfig': {}},
    ]
    assert kafka_default_mode(ctx)['usage'] == 3


def test_lambda_direct_upload_size_requires_upload_provenance():
    # GetFunction reports CodeSize and PackageType, but both direct ZIP and
    # S3-backed ZIP deployments have the same observable inventory shape.
    with pytest.raises(Unsupported, match='direct-vs-S3 upload provenance'):
        direct_upload_package_size(Mock())


def test_account_inventory_filter_is_applied():
    from modules.qmchecks.vpc.vpc import inventory
    ctx = Mock(account='123456789012')
    ctx.call.return_value = []
    inventory(ctx, 'describe_security_groups', 'SecurityGroups')
    assert ctx.call.call_args.kwargs['Filters'] == [{'Name': 'owner-id', 'Values': ['123456789012']}]


def test_nat_per_vpc_uses_nat_vpc_id_and_subnet_fallback():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'SubnetId': 's1', 'VpcId': 'vpc-1'}, {'SubnetId': 's2', 'VpcId': 'vpc-2'}],
        [{'NatGatewayId': 'n1', 'VpcId': 'vpc-1', 'SubnetId': 's1', 'State': 'available'},
         {'NatGatewayId': 'n2', 'SubnetId': 's2', 'State': 'available'},
         {'NatGatewayId': 'n3', 'VpcId': 'vpc-1', 'State': 'deleted'}],
    ]
    result = nat_per_vpc(ctx)
    assert result['usage'] == 1 and result['resource_id'] == 'vpc-1'


def test_ram_ou_participants_expand_organization_members():
    ctx = Mock(account='111111111111')
    def calls(service, method, key=None, **kwargs):
        if method == 'describe_subnets':
            return [{'SubnetId': 's1', 'VpcId': 'vpc-1'}]
        if method == 'list_resources':
            return [{'arn': 'arn:subnet/s1', 'resourceShareArn': 'share'}]
        if method == 'list_principals':
            return [{'id': 'ou-abc'}]
        if method == 'list_accounts_for_parent':
            return [{'Id': '222222222222'}]
        if method == 'list_organizational_units_for_parent':
            return []
        return []
    ctx.call.side_effect = calls
    assert participants(ctx)['usage'] == 1
