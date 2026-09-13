"""AWS App Mesh regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


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
]


def get_current_quotastatus_appmesh(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appmesh' for service, _ in context.quotas):
        return []
    return context.run('appmesh', CHECKS, skip)
