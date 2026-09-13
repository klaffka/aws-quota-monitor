"""Regional REST API Gateway quota inventories.

The fixed API-count quotas apply to REST APIs and endpoint types. HTTP and
WebSocket APIs are deliberately excluded because they are governed by
different API Gateway quota families.
"""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def rest_apis(ctx):
    return ctx.call('apigateway', 'get_rest_apis', 'items')


def endpoint_count(ctx, endpoint_type):
    return dict(usage=sum(endpoint_type in api.get('endpointConfiguration', {}).get('types', [])
                          for api in rest_apis(ctx)),
                source='apigateway:GetRestApis', method='ACCOUNT_COUNT')


def stages_per_api(ctx):
    values = []
    for api in rest_apis(ctx):
        api_id = api['id']
        stages = ctx.call('apigateway', 'get_stages', 'item', restApiId=api_id)
        values.append((api_id, len(stages), None))
    return maximum(values, 'RestApi', 'apigateway:GetStages')


def portal_products(ctx):
    return ctx.call('apigatewayv2', 'list_portal_products', 'Items')


def portals(ctx):
    return ctx.call('apigatewayv2', 'list_portals', 'Items')


def portal_products_per_portal(ctx):
    values = []
    for portal in portals(ctx):
        portal_id = portal.get('PortalId') or portal.get('portalId')
        if not portal_id:
            continue
        detail = ctx.call('apigatewayv2', 'get_portal', PortalId=portal_id)
        products = detail.get('IncludedPortalProductArns') or []
        values.append((portal_id, len(products), None))
    return maximum(values, 'APIGatewayPortal', 'apigatewayv2:GetPortal')


def _pages_per_product(ctx, method, key):
    values = []
    for product in portal_products(ctx):
        product_id = product.get('PortalProductId') or product.get('portalProductId')
        if not product_id:
            continue
        pages = ctx.call('apigatewayv2', method, 'Items', PortalProductId=product_id)
        values.append((product_id, len(pages), None))
    return maximum(values, 'APIGatewayPortalProduct', f'apigatewayv2:{method}')


def product_pages_per_product(ctx):
    return _pages_per_product(ctx, 'list_product_pages', 'Items')


def product_rest_endpoint_pages_per_product(ctx):
    return _pages_per_product(ctx, 'list_product_rest_endpoint_pages', 'Items')


CHECKS = [
    ('L-AA0FF27B', 'Regional APIs', lambda ctx: endpoint_count(ctx, 'REGIONAL')),
    ('L-B97207D0', 'Edge-optimized APIs', lambda ctx: endpoint_count(ctx, 'EDGE')),
    ('L-A966AB5C', 'Private APIs', lambda ctx: endpoint_count(ctx, 'PRIVATE')),
    ('L-379E48B0', 'Stages per API', stages_per_api),
    ('L-7D4D47CD', 'Portal products per account',
     lambda ctx: dict(usage=len(portal_products(ctx)), source='apigatewayv2:ListPortalProducts', method='ACCOUNT_COUNT')),
    ('L-F8BD84D3', 'Portals per account',
     lambda ctx: dict(usage=len(portals(ctx)), source='apigatewayv2:ListPortals', method='ACCOUNT_COUNT')),
    ('L-85120D8E', 'Portal products per portal', portal_products_per_portal),
    ('L-154598D1', 'Product pages per portal product', product_pages_per_product),
    ('L-05295E0B', 'Product REST endpoint pages per portal product', product_rest_endpoint_pages_per_product),
]


def get_current_quotastatus_apigateway(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'apigateway' for service, _ in context.quotas):
        return []
    return context.run('apigateway', CHECKS, skip)
