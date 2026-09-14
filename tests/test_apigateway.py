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
