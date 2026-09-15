"""API Gateway REST, HTTP and WebSocket inventories and per-API structures.

The payload, header, URL and template size quotas bound a single request or
document, the timeout and TTL quotas name a period, and the WebSocket
connection duration and idle timeout describe one connection's lifetime.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

APIGATEWAY = 'apigateway'
APIGATEWAYV2 = 'apigatewayv2'


def rest_apis(ctx):
    return ctx.call(APIGATEWAY, 'get_rest_apis', 'items')


def _identity(item, field, subject):
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise NoData(f'API Gateway {subject} is missing its identity')
    return value


def http_apis(ctx, protocol):
    """Return the V2 APIs speaking one protocol, keyed by API id."""
    found = {}
    for api in ctx.call(APIGATEWAYV2, 'get_apis', 'Items'):
        if api.get('ProtocolType') != protocol:
            continue
        found[_identity(api, 'ApiId', 'API')] = api
    return found


def _account_count(service, method, key, source):
    return lambda ctx: dict(usage=len(ctx.call(service, method, key)),
                            source=source, method='ACCOUNT_COUNT')


def private_domain_names(ctx):
    usage = 0
    for domain in ctx.call(APIGATEWAY, 'get_domain_names', 'items'):
        configuration = domain.get('endpointConfiguration') or {}
        types = configuration.get('types') or []
        if not isinstance(types, list):
            raise NoData('API Gateway domain name has an invalid endpoint type')
        usage += 'PRIVATE' in types
    return dict(usage=usage, source='apigateway:GetDomainNames',
                method='ACCOUNT_COUNT')


def usage_plans_per_api_key(ctx):
    """Invert the per-plan key listing, which is the only direction AWS offers."""
    counts = Counter()
    for plan in ctx.call(APIGATEWAY, 'get_usage_plans', 'items'):
        identity = _identity(plan, 'id', 'usage plan')
        for key in ctx.call(APIGATEWAY, 'get_usage_plan_keys', 'items',
                            usagePlanId=identity):
            counts[_identity(key, 'id', 'usage plan key')] += 1
    return maximum(((key, count, None) for key, count in counts.items()),
                   'ApiKey', 'apigateway:GetUsagePlanKeys')


def subnets_per_vpc_link(ctx):
    values = []
    for link in ctx.call(APIGATEWAYV2, 'get_vpc_links', 'Items'):
        identity = _identity(link, 'VpcLinkId', 'VPC link')
        detail = ctx.call(APIGATEWAYV2, 'get_vpc_link', VpcLinkId=identity)
        subnets = detail.get('SubnetIds')
        if not isinstance(subnets, list):
            raise NoData('API Gateway VPC link has no subnets')
        values.append((identity, len(subnets), None))
    return maximum(values, 'VpcLink', 'apigatewayv2:GetVpcLink')


def resources_or_routes_per_api(ctx):
    """REST resources and WebSocket routes share one quota."""
    values = []
    for api in rest_apis(ctx):
        identity = _identity(api, 'id', 'REST API')
        resources = ctx.call(APIGATEWAY, 'get_resources', 'items', restApiId=identity)
        values.append((identity, len(resources), None))
    for identity in http_apis(ctx, 'WEBSOCKET'):
        routes = ctx.call(APIGATEWAYV2, 'get_routes', 'Items', ApiId=identity)
        values.append((identity, len(routes), None))
    return maximum(values, 'Api', 'apigateway:GetResources+apigatewayv2:GetRoutes')


def routes_per_http_api(ctx):
    values = [(identity, len(ctx.call(APIGATEWAYV2, 'get_routes', 'Items',
                                      ApiId=identity)), None)
              for identity in http_apis(ctx, 'HTTP')]
    return maximum(values, 'HttpApi', 'apigatewayv2:GetRoutes')


def _stage_maximum(field, subject):
    def check(ctx):
        values = []
        for api in rest_apis(ctx):
            identity = _identity(api, 'id', 'REST API')
            for stage in ctx.call(APIGATEWAY, 'get_stages', 'item',
                                  restApiId=identity):
                entries = stage.get(field) or {}
                if not isinstance(entries, dict):
                    raise NoData(f'API Gateway stage has an invalid {subject}')
                values.append((f"{identity}/{stage.get('stageName')}",
                               len(entries), None))
        return maximum(values, 'Stage', 'apigateway:GetStages')
    return check


def endpoint_count(ctx, endpoint_type):
    return dict(usage=sum(endpoint_type in api.get('endpointConfiguration', {}).get('types', [])
                          for api in rest_apis(ctx)),
                source='apigateway:GetRestApis', method='ACCOUNT_COUNT')


def stages_per_api(ctx):
    values = []
    for api in rest_apis(ctx):
        api_id = api['id']
        stages = ctx.call(APIGATEWAY, 'get_stages', 'item', restApiId=api_id)
        values.append((api_id, len(stages), None))
    return maximum(values, 'RestApi', 'apigateway:GetStages')


def portal_products(ctx):
    return ctx.call(APIGATEWAYV2, 'list_portal_products', 'Items')


def portals(ctx):
    return ctx.call(APIGATEWAYV2, 'list_portals', 'Items')


def portal_products_per_portal(ctx):
    values = []
    for portal in portals(ctx):
        portal_id = portal.get('PortalId') or portal.get('portalId')
        if not portal_id:
            continue
        detail = ctx.call(APIGATEWAYV2, 'get_portal', PortalId=portal_id)
        products = detail.get('IncludedPortalProductArns') or []
        values.append((portal_id, len(products), None))
    return maximum(values, 'APIGatewayPortal', 'apigatewayv2:GetPortal')


def _pages_per_product(ctx, method, key):
    values = []
    for product in portal_products(ctx):
        product_id = product.get('PortalProductId') or product.get('portalProductId')
        if not product_id:
            continue
        pages = ctx.call(APIGATEWAYV2, method, 'Items', PortalProductId=product_id)
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
    ('L-7D4D47CD', 'PortalProducts per account',
     lambda ctx: dict(usage=len(portal_products(ctx)), source='apigatewayv2:ListPortalProducts', method='ACCOUNT_COUNT')),
    ('L-F8BD84D3', 'Portals per account',
     lambda ctx: dict(usage=len(portals(ctx)), source='apigatewayv2:ListPortals', method='ACCOUNT_COUNT')),
    ('L-85120D8E', 'PortalProducts per Portal', portal_products_per_portal),
    ('L-154598D1', 'ProductPages per PortalProduct', product_pages_per_product),
    ('L-05295E0B', 'ProductRestEndpointPages per PortalProduct', product_rest_endpoint_pages_per_product),
    ('L-1D180A63', 'API keys',
     _account_count(APIGATEWAY, 'get_api_keys', 'items', 'apigateway:GetApiKeys')),
    ('L-824C9E42', 'Client certificates',
     _account_count(APIGATEWAY, 'get_client_certificates', 'items',
                    'apigateway:GetClientCertificates')),
    ('L-A93447B8', 'Custom Domain Names',
     _account_count(APIGATEWAY, 'get_domain_names', 'items',
                    'apigateway:GetDomainNames')),
    ('L-24E7E662', 'Private custom domain names', private_domain_names),
    ('L-4D98A8A5', 'Domain name access associations',
     _account_count(APIGATEWAY, 'get_domain_name_access_associations', 'items',
                    'apigateway:GetDomainNameAccessAssociations')),
    ('L-E8693075', 'Usage plans',
     _account_count(APIGATEWAY, 'get_usage_plans', 'items',
                    'apigateway:GetUsagePlans')),
    ('L-985EB478', 'Usage plans per API key', usage_plans_per_api_key),
    ('L-A4C7274F', 'VPC links',
     _account_count(APIGATEWAY, 'get_vpc_links', 'items', 'apigateway:GetVpcLinks')),
    ('L-608BDCD4', 'VPC links(V2)',
     _account_count(APIGATEWAYV2, 'get_vpc_links', 'Items',
                    'apigatewayv2:GetVpcLinks')),
    ('L-668C9B28', 'Subnets per VPC link(V2)', subnets_per_vpc_link),
    ('L-01C8A9E0', 'Resources/Routes per REST/WebSocket API',
     resources_or_routes_per_api),
    ('L-65B5C802', 'Routes per HTTP API', routes_per_http_api),
    ('L-95BA6EA5', 'Stage variables per stage',
     _stage_maximum('variables', 'variable map')),
    ('L-FB4F0270', 'Tags Per Stage', _stage_maximum('tags', 'tag map')),
]


def get_current_quotastatus_apigateway(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'apigateway' for service, _ in context.quotas):
        return []
    return context.run('apigateway', CHECKS, skip)
