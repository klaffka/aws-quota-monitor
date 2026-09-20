"""AWS App Mesh regional resource-count and specification quotas.

A virtual node's backends and a route's weighted targets live in the
specification rather than in a listing, so each is read from the detail of the
resources the counts beside them already walk.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

# A route spec names exactly one of these, and each puts its targets under the
# same action member.
ROUTE_KINDS = ('grpcRoute', 'http2Route', 'httpRoute', 'tcpRoute')


def meshes(ctx):
    return ctx.call('appmesh', 'list_meshes', 'meshes')


def mesh_resources(ctx, method, key, name_key, resource_type):
    values = []
    for mesh in meshes(ctx):
        name = mesh.get('meshName')
        resources = ctx.call('appmesh', method, key, meshName=name)
        values.append((name, len(resources), None))
    return maximum(values, resource_type, f'appmesh:{method}')


def routes_per_router(ctx):
    values = []
    for mesh in meshes(ctx):
        mesh_name = mesh.get('meshName')
        routers = ctx.call('appmesh', 'list_virtual_routers', 'virtualRouters', meshName=mesh_name)
        for router in routers:
            name = router.get('virtualRouterName')
            routes = ctx.call('appmesh', 'list_routes', 'routes', meshName=mesh_name,
                              virtualRouterName=name)
            values.append((f'{mesh_name}/{name}', len(routes), None))
    return maximum(values, 'VirtualRouter', 'appmesh:ListRoutes')


def gateway_routes_per_gateway(ctx):
    values = []
    for mesh in meshes(ctx):
        mesh_name = mesh.get('meshName')
        gateways = ctx.call('appmesh', 'list_virtual_gateways', 'virtualGateways', meshName=mesh_name)
        for gateway in gateways:
            name = gateway.get('virtualGatewayName')
            routes = ctx.call('appmesh', 'list_gateway_routes', 'gatewayRoutes', meshName=mesh_name,
                              virtualGatewayName=name)
            values.append((f'{mesh_name}/{name}', len(routes), None))
    return maximum(values, 'VirtualGateway', 'appmesh:ListGatewayRoutes')


def backends_per_virtual_node(ctx):
    """A virtual node calling nothing has no backend, which is zero."""
    values = []
    for mesh in meshes(ctx):
        mesh_name = mesh.get('meshName')
        for node in ctx.call('appmesh', 'list_virtual_nodes', 'virtualNodes',
                             meshName=mesh_name):
            name = node.get('virtualNodeName')
            if not isinstance(name, str) or not name:
                raise NoData('App Mesh virtual node is missing its name')
            detail = ctx.call('appmesh', 'describe_virtual_node', meshName=mesh_name,
                              virtualNodeName=name).get('virtualNode') or {}
            backends = (detail.get('spec') or {}).get('backends') or []
            values.append((f'{mesh_name}/{name}', len(backends), None))
    return maximum(values, 'VirtualNode', 'appmesh:DescribeVirtualNode')


def weighted_targets_per_route(ctx):
    values = []
    for mesh in meshes(ctx):
        mesh_name = mesh.get('meshName')
        for router in ctx.call('appmesh', 'list_virtual_routers', 'virtualRouters',
                               meshName=mesh_name):
            router_name = router.get('virtualRouterName')
            for route in ctx.call('appmesh', 'list_routes', 'routes',
                                  meshName=mesh_name,
                                  virtualRouterName=router_name):
                name = route.get('routeName')
                if not isinstance(name, str) or not name:
                    raise NoData('App Mesh route is missing its name')
                detail = ctx.call('appmesh', 'describe_route', meshName=mesh_name,
                                  virtualRouterName=router_name,
                                  routeName=name).get('route') or {}
                spec = detail.get('spec') or {}
                usage = sum(len(((spec.get(kind) or {}).get('action') or {})
                                .get('weightedTargets') or ())
                            for kind in ROUTE_KINDS)
                values.append((f'{mesh_name}/{router_name}/{name}', usage, None))
    return maximum(values, 'Route', 'appmesh:DescribeRoute')


CHECKS = [
    ('L-AC861A39', 'Meshes per account',
     lambda ctx: dict(usage=len(meshes(ctx)), source='appmesh:ListMeshes', method='ACCOUNT_COUNT')),
    ('L-DA7495A7', 'Virtual services per mesh',
     lambda ctx: mesh_resources(ctx, 'list_virtual_services', 'virtualServices', 'virtualServiceName', 'Mesh')),
    ('L-87E74146', 'Virtual gateways per mesh',
     lambda ctx: mesh_resources(ctx, 'list_virtual_gateways', 'virtualGateways', 'virtualGatewayName', 'Mesh')),
    ('L-50F6C35A', 'Virtual routers per mesh',
     lambda ctx: mesh_resources(ctx, 'list_virtual_routers', 'virtualRouters', 'virtualRouterName', 'Mesh')),
    ('L-E043DFB4', 'Virtual nodes per mesh',
     lambda ctx: mesh_resources(ctx, 'list_virtual_nodes', 'virtualNodes', 'virtualNodeName', 'Mesh')),
    ('L-BB90B7FF', 'Routes per virtual router', routes_per_router),
    ('L-F6F26D09', 'Gateway routes per virtual gateway', gateway_routes_per_gateway),
    ('L-8775AB18', 'Backends per virtual node', backends_per_virtual_node),
    ('L-AE1D9567', 'Weighted targets per route', weighted_targets_per_route),
]


def get_current_quotastatus_appmesh(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appmesh' for service, _ in context.quotas):
        return []
    return context.run('appmesh', CHECKS, skip)
