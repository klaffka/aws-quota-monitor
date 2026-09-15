import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.ec2 import ec2
from modules.qmcore.aws import CheckContext, NoData

GATEWAY = 'tgw-11111111111111111'
OTHER_GATEWAY = 'tgw-22222222222222222'
DOMAIN = 'tgw-mcast-domain-11111111111111111'
OTHER_DOMAIN = 'tgw-mcast-domain-22222222222222222'
VPC = 'vpc-11111111111111111'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ec2', 'QuotaCode': code, 'Value': 20}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in ec2.CHECKS if candidate == code)


def domain(identity, gateway, state='available'):
    return {'TransitGatewayMulticastDomainId': identity,
            'TransitGatewayId': gateway, 'State': state}


def group(address, member=False, source=False, interface=None):
    entry = {'GroupIpAddress': address, 'GroupMember': member,
             'GroupSource': source}
    if interface:
        entry['NetworkInterfaceId'] = interface
    return entry


def test_deleted_multicast_domains_do_not_count():
    ctx = context('L-31775423')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_transit_gateway_multicast_domains', {
            'TransitGatewayMulticastDomains': [
                domain(DOMAIN, GATEWAY), domain(OTHER_DOMAIN, GATEWAY),
                domain('tgw-mcast-domain-33333333333333333', OTHER_GATEWAY,
                       'deleted')]}, {})
        result = check('L-31775423')(ctx)
        assert (result['usage'], result['resource_id']) == (2, GATEWAY)
        stub.assert_no_pending_responses()


def test_sources_and_members_are_counted_per_group():
    ctx = context('L-4F2F99E3')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_transit_gateway_multicast_domains',
                          {'TransitGatewayMulticastDomains': [
                              domain(DOMAIN, GATEWAY)]}, {})
        stub.add_response('search_transit_gateway_multicast_groups', {
            'MulticastGroups': [
                group('224.0.0.1', source=True, interface='eni-1'),
                group('224.0.0.1', source=True, interface='eni-2'),
                group('224.0.0.1', member=True, interface='eni-3'),
                group('224.0.0.2', member=True, interface='eni-1')]},
            {'TransitGatewayMulticastDomainId': DOMAIN})
        sources = check('L-4F2F99E3')(ctx)
        assert (sources['usage'], sources['resource_id']) == (2, f'{DOMAIN}/224.0.0.1')
        members = check('L-C768F2D6')(ctx)
        assert members['usage'] == 1
        # One interface serves two groups but counts once for the gateway.
        interfaces = check('L-C673935A')(ctx)
        assert (interfaces['usage'], interfaces['resource_id']) == (3, GATEWAY)
        stub.assert_no_pending_responses()


def test_a_group_without_an_address_raises_nodata():
    ctx = context('L-4F2F99E3')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_transit_gateway_multicast_domains',
                          {'TransitGatewayMulticastDomains': [
                              domain(DOMAIN, GATEWAY)]}, {})
        stub.add_response('search_transit_gateway_multicast_groups',
                          {'MulticastGroups': [{'GroupSource': True}]},
                          {'TransitGatewayMulticastDomainId': DOMAIN})
        with pytest.raises(NoData, match='no group address'):
            check('L-4F2F99E3')(ctx)


def test_domain_associations_are_counted_per_vpc():
    ctx = context('L-9F8FA74B')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_transit_gateway_multicast_domains',
                          {'TransitGatewayMulticastDomains': [
                              domain(DOMAIN, GATEWAY)]}, {})
        stub.add_response('get_transit_gateway_multicast_domain_associations', {
            'MulticastDomainAssociations': [
                {'ResourceType': 'vpc', 'ResourceId': VPC},
                {'ResourceType': 'vpc', 'ResourceId': VPC},
                {'ResourceType': 'vpn', 'ResourceId': 'vpn-1'}]},
            {'TransitGatewayMulticastDomainId': DOMAIN})
        result = check('L-9F8FA74B')(ctx)
        assert (result['usage'], result['resource_id']) == (2, VPC)
        stub.assert_no_pending_responses()


def attachment(identity, gateway, resource, resource_type, state='available'):
    return {'TransitGatewayAttachmentId': identity, 'TransitGatewayId': gateway,
            'ResourceId': resource, 'ResourceType': resource_type, 'State': state}


def test_attachments_are_counted_from_both_ends_and_skip_deleted():
    ctx = context('L-350B2172')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_transit_gateway_attachments', {
            'TransitGatewayAttachments': [
                attachment('tgw-attach-1', GATEWAY, 'dxgw-1',
                           'direct-connect-gateway'),
                attachment('tgw-attach-2', GATEWAY, 'dxgw-2',
                           'direct-connect-gateway'),
                attachment('tgw-attach-3', OTHER_GATEWAY, 'dxgw-1',
                           'direct-connect-gateway'),
                attachment('tgw-attach-4', GATEWAY, 'dxgw-3',
                           'direct-connect-gateway', 'deleted'),
                attachment('tgw-attach-5', GATEWAY, VPC, 'vpc')]}, {})
        per_gateway = check('L-350B2172')(ctx)
        assert (per_gateway['usage'], per_gateway['resource_id']) == (2, GATEWAY)
        per_dxgw = check('L-6B192186')(ctx)
        assert (per_dxgw['usage'], per_dxgw['resource_id']) == (2, 'dxgw-1')
        per_vpc = check('L-6DA43717')(ctx)
        assert (per_vpc['usage'], per_vpc['resource_id']) == (1, VPC)
        stub.assert_no_pending_responses()


def test_fpga_images_are_limited_to_this_account():
    ctx = context('L-8FBBDF0C')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_fpga_images', {'FpgaImages': [
            {'FpgaImageId': 'afi-1'}, {'FpgaImageId': 'afi-2'}]},
            {'Owners': ['self']})
        assert check('L-8FBBDF0C')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
