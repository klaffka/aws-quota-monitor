from unittest.mock import Mock

from modules.qmchecks.apigateway import (
    endpoint_count, stages_per_api, portal_products_per_portal,
    product_pages_per_product, product_rest_endpoint_pages_per_product,
)


def test_api_gateway_counts_rest_endpoint_types_only():
    ctx = Mock()
    ctx.call.return_value = [
        {'id': 'regional', 'endpointConfiguration': {'types': ['REGIONAL']}},
        {'id': 'edge', 'endpointConfiguration': {'types': ['EDGE']}},
        {'id': 'private', 'endpointConfiguration': {'types': ['PRIVATE']}},
    ]
    assert endpoint_count(ctx, 'REGIONAL')['usage'] == 1
    assert endpoint_count(ctx, 'EDGE')['usage'] == 1
    assert endpoint_count(ctx, 'PRIVATE')['usage'] == 1


def test_api_gateway_stages_use_maximum_per_rest_api():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'api-1'}, {'id': 'api-2'}],
        [{'stageName': 'one'}, {'stageName': 'two'}],
        [{'stageName': 'one'}],
    ]
    result = stages_per_api(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'api-1')


def test_api_gateway_v2_portal_child_counts_use_parent_maxima():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'PortalId': 'portal-1'}, {'PortalId': 'portal-2'}],
        {'IncludedPortalProductArns': ['arn:product:1', 'arn:product:2']},
        {'IncludedPortalProductArns': ['arn:product:3']},
    ]
    result = portal_products_per_portal(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'portal-1')


def test_api_gateway_v2_product_page_counts_are_paginated_per_product():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'PortalProductId': 'product-1'}, {'PortalProductId': 'product-2'}],
        [{'ProductPageId': 'page-1'}, {'ProductPageId': 'page-2'}],
        [{'ProductPageId': 'page-3'}],
    ]
    result = product_pages_per_product(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'product-1')

    ctx = Mock()
    ctx.call.side_effect = [
        [{'PortalProductId': 'product-1'}],
        [{'ProductRestEndpointPageId': 'page-1'}],
    ]
    result = product_rest_endpoint_pages_per_product(ctx)
    assert (result['usage'], result['resource_id']) == (1, 'product-1')


def stubbed(code):
    import boto3
    from modules.qmcore.aws import CheckContext
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'apigateway', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def apigateway_check(code):
    from modules.qmchecks.apigateway import CHECKS
    return next(fn for quota, _, fn in CHECKS if quota == code)


def test_private_domain_names_are_counted_by_endpoint_type():
    from botocore.stub import Stubber
    from modules.qmchecks.apigateway import private_domain_names

    ctx = stubbed('L-24E7E662')
    with Stubber(ctx.client('apigateway')) as stub:
        stub.add_response('get_domain_names', {'items': [
            {'domainName': 'a.example',
             'endpointConfiguration': {'types': ['PRIVATE']}},
            {'domainName': 'b.example',
             'endpointConfiguration': {'types': ['REGIONAL']}}]}, {})
        assert private_domain_names(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_usage_plans_per_api_key_invert_the_per_plan_listing():
    from botocore.stub import Stubber
    from modules.qmchecks.apigateway import usage_plans_per_api_key

    ctx = stubbed('L-985EB478')
    with Stubber(ctx.client('apigateway')) as stub:
        stub.add_response('get_usage_plans', {'items': [
            {'id': 'plan-1', 'name': 'basic'}, {'id': 'plan-2', 'name': 'pro'}]}, {})
        stub.add_response('get_usage_plan_keys', {'items': [
            {'id': 'key-1', 'type': 'API_KEY'}]}, {'usagePlanId': 'plan-1'})
        stub.add_response('get_usage_plan_keys', {'items': [
            {'id': 'key-1', 'type': 'API_KEY'}, {'id': 'key-2', 'type': 'API_KEY'}]},
            {'usagePlanId': 'plan-2'})
        result = usage_plans_per_api_key(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'key-1')
        stub.assert_no_pending_responses()


def test_rest_resources_and_websocket_routes_share_one_quota():
    from botocore.stub import Stubber
    from modules.qmchecks.apigateway import resources_or_routes_per_api

    ctx = stubbed('L-01C8A9E0')
    rest = Stubber(ctx.client('apigateway'))
    v2 = Stubber(ctx.client('apigatewayv2'))
    with rest as rest_stub, v2 as v2_stub:
        rest_stub.add_response('get_rest_apis', {'items': [{'id': 'rest-1'}]}, {})
        rest_stub.add_response('get_resources', {'items': [
            {'id': 'r1'}, {'id': 'r2'}]}, {'restApiId': 'rest-1'})
        v2_stub.add_response('get_apis', {'Items': [
            {'ApiId': 'ws-1', 'Name': 'socket', 'ProtocolType': 'WEBSOCKET',
             'RouteSelectionExpression': '$request.body.action'},
            {'ApiId': 'http-1', 'Name': 'http', 'ProtocolType': 'HTTP',
             'RouteSelectionExpression': '$request.method $request.path'}]}, {})
        v2_stub.add_response('get_routes', {'Items': [
            {'RouteId': 'a', 'RouteKey': '$connect'},
            {'RouteId': 'b', 'RouteKey': '$disconnect'},
            {'RouteId': 'c', 'RouteKey': 'message'}]}, {'ApiId': 'ws-1'})
        result = resources_or_routes_per_api(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'ws-1')
        rest_stub.assert_no_pending_responses()
        v2_stub.assert_no_pending_responses()


def test_stage_variables_and_tags_are_counted_per_stage():
    from botocore.stub import Stubber

    for code, field, expected in (('L-95BA6EA5', 'variables', 2),
                                  ('L-FB4F0270', 'tags', 3)):
        ctx = stubbed(code)
        with Stubber(ctx.client('apigateway')) as stub:
            stub.add_response('get_rest_apis', {'items': [{'id': 'rest-1'}]}, {})
            stub.add_response('get_stages', {'item': [
                {'stageName': 'prod', 'variables': {'a': '1', 'b': '2'},
                 'tags': {'x': '1', 'y': '2', 'z': '3'}}]}, {'restApiId': 'rest-1'})
            result = apigateway_check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected,
                                                                'rest-1/prod'), field
            stub.assert_no_pending_responses()
