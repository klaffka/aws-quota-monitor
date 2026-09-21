"""Three scopes that ride listings their modules already walk, plus m2 storage."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import groundstation, m2, media_extra
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def group_id(name):
    """A dataflow endpoint group id is at least 36 characters."""
    return f'dfeg-{name}'.ljust(36, '0')


def test_dataflow_endpoint_groups_are_counted_from_the_listing():
    ctx = context('groundstation', 'L-D6A1915B')
    with Stubber(ctx.client('groundstation')) as stub:
        stub.add_response('list_dataflow_endpoint_groups', {
            'dataflowEndpointGroupList': [
                {'dataflowEndpointGroupId': group_id('one')},
                {'dataflowEndpointGroupId': group_id('two')}]}, {})
        result = check(groundstation, 'L-D6A1915B')(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_an_account_without_dataflow_endpoint_groups_counts_as_zero():
    ctx = context('groundstation', 'L-D6A1915B')
    with Stubber(ctx.client('groundstation')) as stub:
        stub.add_response('list_dataflow_endpoint_groups',
                          {'dataflowEndpointGroupList': []}, {})
        assert check(groundstation, 'L-D6A1915B')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def endpoint(name, hls=0, low_latency=0, dash=0, mss=0):
    """An origin endpoint; the listing already carries every manifest kind."""
    return {'Arn': f'arn:endpoint/{name}', 'ChannelGroupName': 'group',
            'ChannelName': 'channel', 'OriginEndpointName': name,
            'ContainerType': 'TS',
            'HlsManifests': [{'ManifestName': f'h{i}'} for i in range(hls)],
            'LowLatencyHlsManifests': [{'ManifestName': f'l{i}'}
                                       for i in range(low_latency)],
            'DashManifests': [{'ManifestName': f'd{i}'} for i in range(dash)],
            'MssManifests': [{'ManifestName': f'm{i}'} for i in range(mss)]}


def stub_endpoints(stub, endpoints):
    stub.add_response('list_channel_groups',
                      {'Items': [{'ChannelGroupName': 'group',
                                  'Arn': 'arn:group', 'CreatedAt': 1,
                                  'ModifiedAt': 1}]}, {})
    stub.add_response('list_channels', {'Items': [
        {'ChannelName': 'channel', 'Arn': 'arn:channel', 'ChannelGroupName': 'group',
         'CreatedAt': 1, 'ModifiedAt': 1}]}, {'ChannelGroupName': 'group'})
    stub.add_response('list_origin_endpoints', {'Items': list(endpoints)},
                      {'ChannelGroupName': 'group', 'ChannelName': 'channel'})


def media_check(code):
    """The MediaPackage V2 checks are built where the collector calls them."""
    return next(fn for quota, _name, fn in media_extra.MEDIAPACKAGEV2_CHECKS
                if quota == code)


def test_every_kind_of_manifest_counts_towards_the_endpoint_total():
    ctx = context('mediapackagev2', 'L-0FB78A52')
    with Stubber(ctx.client('mediapackagev2')) as stub:
        stub_endpoints(stub, [endpoint('quiet', hls=1),
                              endpoint('busy', hls=1, low_latency=1, dash=2)])
        result = media_check('L-0FB78A52')(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'busy')
        stub.assert_no_pending_responses()


def test_an_endpoint_publishing_no_manifest_counts_as_zero():
    ctx = context('mediapackagev2', 'L-0FB78A52')
    with Stubber(ctx.client('mediapackagev2')) as stub:
        stub_endpoints(stub, [endpoint('bare')])
        result = media_check('L-0FB78A52')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


def stub_environments(stub, environments):
    """Stub the environment listing, then one detail per environment."""
    stub.add_response('list_environments', {'environments': [
        {'name': name, 'environmentId': name, 'environmentArn': f'arn:env/{name}',
         'engineType': 'bluage', 'engineVersion': '1',
         'instanceType': 'M2.m5.large', 'status': 'Available',
         'creationTime': 1} for name in environments]}, {})
    for name, storage in environments.items():
        stub.add_response('get_environment', {
            'name': name, 'environmentId': name, 'environmentArn': f'arn:env/{name}',
            'engineType': 'bluage', 'engineVersion': '1', 'instanceType': 'M2.m5.large',
            'status': 'Available', 'creationTime': 1,
            'vpcId': 'vpc-1', 'subnetIds': ['subnet-1'], 'securityGroupIds': ['sg-1'],
            'storageConfigurations': list(storage)}, {'environmentId': name})


def efs(name):
    return {'efs': {'fileSystemId': name, 'mountPoint': f'/mnt/{name}'}}


def fsx(name):
    return {'fsx': {'fileSystemId': name, 'mountPoint': f'/mnt/{name}'}}


def test_efs_and_fsx_filesystems_are_counted_apart():
    ctx = context('m2', 'L-5D943D0B')
    with Stubber(ctx.client('m2')) as stub:
        stub_environments(stub, {'one': [efs('a'), efs('b'), fsx('c')]})
        result = check(m2, 'L-5D943D0B')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'one')
        stub.assert_no_pending_responses()


def test_the_fsx_scope_counts_only_fsx():
    ctx = context('m2', 'L-C1C41257')
    with Stubber(ctx.client('m2')) as stub:
        stub_environments(stub, {'one': [efs('a'), efs('b'), fsx('c')]})
        result = check(m2, 'L-C1C41257')(ctx)
        assert (result['usage'], result['resource_id']) == (1, 'one')
        stub.assert_no_pending_responses()


def test_an_environment_mounting_nothing_counts_as_zero():
    ctx = context('m2', 'L-5D943D0B')
    with Stubber(ctx.client('m2')) as stub:
        stub_environments(stub, {'bare': []})
        result = check(m2, 'L-5D943D0B')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering one listing, for a response the SDK cannot produce."""

    def __init__(self, items):
        self.items = items

    def call(self, _service, _method, _key=None, **_kwargs):
        return self.items


def test_an_environment_without_an_identity_is_reported():
    """The environment id is required, so only a broken response omits it."""
    with pytest.raises(NoData, match='identity'):
        check(m2, 'L-5D943D0B')(FakeContext([{'name': 'nameless'}]))
