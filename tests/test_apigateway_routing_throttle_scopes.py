"""API Gateway routing rules per domain and throttles inside a usage plan."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import apigateway
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': 'apigateway', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _name, fn in apigateway.CHECKS if quota == code)


def stub_domains(stub, domains):
    """Stub the HTTP API domain listing, then the rules of each routing domain.

    ``domains`` maps a domain name to ``(routing mode, rule count)``; a domain
    that only maps APIs is never asked for rules.
    """
    stub.add_response('get_domain_names', {'Items': [
        {'DomainName': name, 'RoutingMode': mode}
        for name, (mode, _) in domains.items()]}, {})
    for name, (mode, rules) in domains.items():
        if mode == 'API_MAPPING_ONLY':
            continue
        stub.add_response('list_routing_rules', {'RoutingRules': [
            {'RoutingRuleId': f'{name}-{index}'} for index in range(rules)]},
            {'DomainName': name})


def test_the_domain_with_the_most_routing_rules_is_measured():
    ctx = context('L-68B79FF0')
    with Stubber(ctx.client('apigatewayv2')) as stub:
        stub_domains(stub, {'quiet.test': ('ROUTING_RULE_ONLY', 1),
                            'busy.test': ('ROUTING_RULE_THEN_API_MAPPING', 4)})
        result = check('L-68B79FF0')(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'busy.test')
        stub.assert_no_pending_responses()


def test_a_domain_that_only_maps_apis_holds_no_routing_rule():
    """A domain outside a routing mode is not asked for rules and counts zero."""
    ctx = context('L-68B79FF0')
    with Stubber(ctx.client('apigatewayv2')) as stub:
        stub_domains(stub, {'plain.test': ('API_MAPPING_ONLY', 0)})
        result = check('L-68B79FF0')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'plain.test')
        stub.assert_no_pending_responses()


def test_an_account_without_domains_counts_as_zero():
    ctx = context('L-68B79FF0')
    with Stubber(ctx.client('apigatewayv2')) as stub:
        stub.add_response('get_domain_names', {'Items': []}, {})
        assert check('L-68B79FF0')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_a_routing_mode_the_sdk_does_not_name_is_reported():
    """A new mode may or may not carry rules, so it is refused rather than read."""
    ctx = context('L-68B79FF0')
    with Stubber(ctx.client('apigatewayv2')) as stub:
        stub.add_response('get_domain_names', {'Items': [
            {'DomainName': 'odd.test', 'RoutingMode': 'FUTURE_MODE'}]}, {})
        with pytest.raises(NoData, match='routing mode'):
            check('L-68B79FF0')(ctx)


def stub_usage_plans(stub, plans):
    """``plans`` maps a plan id to a list of throttle-entry counts per API stage."""
    stub.add_response('get_usage_plans', {'items': [
        {'id': identity, 'name': identity, 'apiStages': [
            {'apiId': f'api{index}', 'stage': 'prod',
             'throttle': {f'/{index}/{entry}/GET': {'rateLimit': 1.0, 'burstLimit': 1}
                          for entry in range(count)}}
            for index, count in enumerate(stages)]}
        for identity, stages in plans.items()]}, {})


def test_throttles_are_summed_across_the_stages_of_a_usage_plan():
    ctx = context('L-A9DBC573')
    with Stubber(ctx.client('apigateway')) as stub:
        stub_usage_plans(stub, {'quiet': [1], 'busy': [2, 3]})
        result = check('L-A9DBC573')(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'busy')
        stub.assert_no_pending_responses()


def test_a_usage_plan_throttling_nothing_counts_as_zero():
    ctx = context('L-A9DBC573')
    with Stubber(ctx.client('apigateway')) as stub:
        stub_usage_plans(stub, {'plain': [0]})
        result = check('L-A9DBC573')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'plain')
        stub.assert_no_pending_responses()


def test_a_usage_plan_with_no_api_stage_counts_as_zero():
    ctx = context('L-A9DBC573')
    with Stubber(ctx.client('apigateway')) as stub:
        stub.add_response('get_usage_plans',
                          {'items': [{'id': 'bare', 'name': 'bare'}]}, {})
        result = check('L-A9DBC573')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


def test_a_usage_plan_without_an_identity_is_reported():
    ctx = context('L-A9DBC573')
    with Stubber(ctx.client('apigateway')) as stub:
        stub.add_response('get_usage_plans', {'items': [{'name': 'nameless'}]}, {})
        with pytest.raises(NoData, match='usage plan'):
            check('L-A9DBC573')(ctx)
