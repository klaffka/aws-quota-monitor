"""App Mesh node and route detail scopes, and CodeArtifact repository upstreams."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import appmesh, codeartifact
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def metadata(arn):
    return {'arn': arn, 'createdAt': 1, 'lastUpdatedAt': 1, 'meshOwner': ACCOUNT,
            'resourceOwner': ACCOUNT, 'uid': 'uid', 'version': 1}


def stub_nodes(stub, nodes):
    """Stub the mesh walk, the node listing and one describe per node."""
    stub.add_response('list_meshes', {'meshes': [
        {'meshName': 'mesh', 'arn': 'arn:mesh', 'createdAt': 1, 'lastUpdatedAt': 1,
         'meshOwner': ACCOUNT, 'resourceOwner': ACCOUNT, 'version': 1}]}, {})
    stub.add_response('list_virtual_nodes', {'virtualNodes': [
        {'virtualNodeName': name, 'meshName': 'mesh', 'arn': f'arn:node/{name}',
         'createdAt': 1, 'lastUpdatedAt': 1, 'meshOwner': ACCOUNT,
         'resourceOwner': ACCOUNT, 'version': 1} for name in nodes]},
        {'meshName': 'mesh'})
    for name, backends in nodes.items():
        stub.add_response('describe_virtual_node', {'virtualNode': {
            'meshName': 'mesh', 'virtualNodeName': name,
            'metadata': metadata(f'arn:node/{name}'),
            'status': {'status': 'ACTIVE'},
            'spec': {'backends': [
                {'virtualService': {'virtualServiceName': f'svc{index}'}}
                for index in range(backends)]}}},
            {'meshName': 'mesh', 'virtualNodeName': name})


def test_the_virtual_node_with_the_most_backends_is_measured():
    ctx = context('appmesh', 'L-8775AB18')
    with Stubber(ctx.client('appmesh')) as stub:
        stub_nodes(stub, {'quiet': 1, 'busy': 4})
        result = check(appmesh, 'L-8775AB18')(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'mesh/busy')
        stub.assert_no_pending_responses()


def test_a_virtual_node_with_no_backend_counts_as_zero():
    ctx = context('appmesh', 'L-8775AB18')
    with Stubber(ctx.client('appmesh')) as stub:
        stub_nodes(stub, {'bare': 0})
        result = check(appmesh, 'L-8775AB18')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'mesh/bare')
        stub.assert_no_pending_responses()


def route_spec(kind, targets):
    """Every kind but tcpRoute also requires a match, which may be empty."""
    route = {'action': {'weightedTargets': [
        {'virtualNode': f'node{index}', 'weight': 1} for index in range(targets)]}}
    if kind != 'tcpRoute':
        route['match'] = {}
    return {kind: route}


def stub_routes(stub, routes):
    """Stub the mesh and router walk, then one describe per route.

    ``routes`` maps a route name to ``(route kind, weighted target count)``.
    """
    stub.add_response('list_meshes', {'meshes': [
        {'meshName': 'mesh', 'arn': 'arn:mesh', 'createdAt': 1, 'lastUpdatedAt': 1,
         'meshOwner': ACCOUNT, 'resourceOwner': ACCOUNT, 'version': 1}]}, {})
    stub.add_response('list_virtual_routers', {'virtualRouters': [
        {'virtualRouterName': 'router', 'meshName': 'mesh', 'arn': 'arn:router',
         'createdAt': 1, 'lastUpdatedAt': 1, 'meshOwner': ACCOUNT,
         'resourceOwner': ACCOUNT, 'version': 1}]}, {'meshName': 'mesh'})
    stub.add_response('list_routes', {'routes': [
        {'routeName': name, 'meshName': 'mesh', 'virtualRouterName': 'router',
         'arn': f'arn:route/{name}', 'createdAt': 1, 'lastUpdatedAt': 1,
         'meshOwner': ACCOUNT, 'resourceOwner': ACCOUNT, 'version': 1}
        for name in routes]}, {'meshName': 'mesh', 'virtualRouterName': 'router'})
    for name, (kind, targets) in routes.items():
        stub.add_response('describe_route', {'route': {
            'meshName': 'mesh', 'routeName': name, 'virtualRouterName': 'router',
            'metadata': metadata(f'arn:route/{name}'),
            'status': {'status': 'ACTIVE'},
            'spec': route_spec(kind, targets)}},
            {'meshName': 'mesh', 'routeName': name, 'virtualRouterName': 'router'})


@pytest.mark.parametrize('kind', ['httpRoute', 'http2Route', 'grpcRoute', 'tcpRoute'])
def test_every_kind_of_route_carries_its_weighted_targets(kind):
    """All four route kinds put the targets under the same action member."""
    ctx = context('appmesh', 'L-AE1D9567')
    with Stubber(ctx.client('appmesh')) as stub:
        stub_routes(stub, {'one': (kind, 3)})
        result = check(appmesh, 'L-AE1D9567')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'mesh/router/one')
        stub.assert_no_pending_responses()


def test_the_busiest_route_is_the_one_measured():
    ctx = context('appmesh', 'L-AE1D9567')
    with Stubber(ctx.client('appmesh')) as stub:
        stub_routes(stub, {'quiet': ('httpRoute', 1), 'busy': ('grpcRoute', 5)})
        result = check(appmesh, 'L-AE1D9567')(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'mesh/router/busy')
        stub.assert_no_pending_responses()


def stub_repositories(stub, repositories):
    stub.add_response('list_domains', {'domains': [{'name': 'domain'}]}, {})
    stub.add_response('list_repositories_in_domain', {'repositories': [
        {'name': name, 'domainName': 'domain'} for name in repositories]},
        {'domain': 'domain'})
    for name, upstreams in repositories.items():
        stub.add_response('describe_repository', {'repository': {
            'name': name, 'domainName': 'domain',
            'upstreams': [{'repositoryName': f'up{index}'}
                          for index in range(upstreams)]}},
            {'domain': 'domain', 'repository': name})


def test_the_repository_with_the_most_direct_upstreams_is_measured():
    ctx = context('codeartifact', 'L-D42B1EF2')
    with Stubber(ctx.client('codeartifact')) as stub:
        stub_repositories(stub, {'quiet': 1, 'busy': 6})
        result = check(codeartifact, 'L-D42B1EF2')(ctx)
        assert (result['usage'], result['resource_id']) == (6, 'domain/busy')
        stub.assert_no_pending_responses()


def test_a_repository_without_upstreams_counts_as_zero():
    ctx = context('codeartifact', 'L-D42B1EF2')
    with Stubber(ctx.client('codeartifact')) as stub:
        stub_repositories(stub, {'bare': 0})
        result = check(codeartifact, 'L-D42B1EF2')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'domain/bare')
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for responses the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_repository_without_a_name_is_reported():
    ctx = FakeContext({'list_domains': [{'name': 'domain'}],
                       'list_repositories_in_domain': [{'domainName': 'domain'}]})
    with pytest.raises(NoData, match='name'):
        check(codeartifact, 'L-D42B1EF2')(ctx)
