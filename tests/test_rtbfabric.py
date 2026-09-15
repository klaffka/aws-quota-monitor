from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import rtbfabric
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)
REQUESTER = 'gw-requester-1'
RESPONDER = 'gw-responder-1'
LINK = 'link-1'
OTHER_LINK = 'link-2'
CERT = ('arn:aws:acm:eu-central-1:123456789012:certificate/'
        '11111111-1111-1111-1111-111111111111')


def rule(identity):
    return {'ruleId': identity, 'priority': 1, 'conditions': {},
            'status': 'ACTIVE', 'createdAt': NOW, 'updatedAt': NOW}


def context(code='L-A6B8AC62'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'rtbfabric', 'QuotaCode': code, 'Value': 50}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in rtbfabric.CHECKS if quota == code)


def gateways(stub, requester=(REQUESTER,), responder=(RESPONDER,)):
    stub.add_response('list_requester_gateways', {'gatewayIds': list(requester)}, {})
    stub.add_response('list_responder_gateways', {'gatewayIds': list(responder)}, {})


def link(identity, gateway=REQUESTER, modules=0):
    return {'linkId': identity, 'gatewayId': gateway, 'peerGatewayId': RESPONDER,
            'status': 'ACTIVE', 'createdAt': NOW, 'updatedAt': NOW,
            'flowModules': [{'name': f'm{index}', 'version': '1'}
                            for index in range(modules)]}


def test_gateways_count_both_sides_without_duplicates():
    ctx = context('L-A6B8AC62')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub, (REQUESTER, 'gw-requester-2'), (RESPONDER, REQUESTER))
        # A gateway listed on both sides is still one gateway.
        assert check('L-A6B8AC62')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_links_are_reported_per_gateway():
    ctx = context('L-76B04EF7')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub)
        stub.add_response('list_links', {'links': [link(LINK)]}, {'gatewayId': REQUESTER})
        stub.add_response('list_links', {'links': [
            link(OTHER_LINK, RESPONDER), link('link-3', RESPONDER)]},
            {'gatewayId': RESPONDER})
        result = check('L-76B04EF7')(ctx)
        assert (result['usage'], result['resource_id']) == (2, RESPONDER)
        stub.assert_no_pending_responses()


def test_certificate_associations_are_counted_per_gateway():
    ctx = context('L-7A1DE2E7')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub)
        stub.add_response('list_certificate_associations', {'certificateAssociations': [
            {'acmCertificateArn': CERT, 'status': 'ASSOCIATED'}]},
            {'gatewayId': REQUESTER})
        stub.add_response('list_certificate_associations',
                          {'certificateAssociations': []}, {'gatewayId': RESPONDER})
        result = check('L-7A1DE2E7')(ctx)
        assert (result['usage'], result['resource_id']) == (1, REQUESTER)
        stub.assert_no_pending_responses()


def test_routing_rules_are_counted_per_link():
    ctx = context('L-E0D1ECDF')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub, (REQUESTER,), ())
        stub.add_response('list_links', {'links': [link(LINK), link(OTHER_LINK)]},
                          {'gatewayId': REQUESTER})
        stub.add_response('list_link_routing_rules', {'rules': [
            rule('rule-1'), rule('rule-2')]}, {'gatewayId': REQUESTER, 'linkId': LINK})
        stub.add_response('list_link_routing_rules', {'rules': [rule('rule-3')]},
                          {'gatewayId': REQUESTER, 'linkId': OTHER_LINK})
        result = check('L-E0D1ECDF')(ctx)
        assert (result['usage'], result['resource_id']) == (2, LINK)
        stub.assert_no_pending_responses()


def test_flow_modules_come_from_the_link_summary():
    ctx = context('L-010B9A72')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub, (REQUESTER,), ())
        stub.add_response('list_links', {'links': [
            link(LINK, modules=3), link(OTHER_LINK, modules=1)]},
            {'gatewayId': REQUESTER})
        result = check('L-010B9A72')(ctx)
        assert (result['usage'], result['resource_id']) == (3, LINK)
        stub.assert_no_pending_responses()


class FakeContext:
    """Return a fixed inventory, to reach validation the SDK shapes forbid."""

    def __init__(self, items):
        self.items = items

    def call(self, *args, **kwargs):
        return self.items


def test_a_gateway_without_an_identity_raises_nodata():
    with pytest.raises(NoData, match='missing its identity'):
        rtbfabric.gateways(FakeContext(['']))


def test_an_empty_region_reports_zero():
    ctx = context('L-76B04EF7')
    with Stubber(ctx.client('rtbfabric')) as stub:
        gateways(stub, (), ())
        result = check('L-76B04EF7')(ctx)
        assert (result['usage'], result['resource_id']) == (0, None)
        stub.assert_no_pending_responses()


def test_every_rtbfabric_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'rtbfabric'}
    assert {code for code, _, _ in rtbfabric.CHECKS} <= registered
