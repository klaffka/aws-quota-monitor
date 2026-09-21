"""Stored-length quotas: a regex pattern, and a time-shifted manifest window."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import media_extra, streaming, waf_regional
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def stub_pattern_sets(stub, sets):
    """``sets`` maps a pattern set id to its list of pattern strings."""
    stub.add_response('list_regex_pattern_sets', {'RegexPatternSets': [
        {'RegexPatternSetId': identity, 'Name': identity} for identity in sets]}, {})
    for identity, patterns in sets.items():
        stub.add_response('get_regex_pattern_set', {'RegexPatternSet': {
            'RegexPatternSetId': identity, 'Name': identity,
            'RegexPatternStrings': list(patterns)}},
            {'RegexPatternSetId': identity})


def waf_check(code):
    return next(fn for quota, _name, fn in waf_regional.CHECKS if quota == code)


def test_the_longest_regex_pattern_is_measured():
    ctx = context('waf-regional', 'L-797E08C8')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub_pattern_sets(stub, {'one': ['^a$'],
                                 'two': ['^b$', '^a-considerably-longer-one$']})
        result = waf_check('L-797E08C8')(ctx)
        assert (result['usage'], result['resource_id']) == (27, 'two')
        stub.assert_no_pending_responses()


def test_a_pattern_set_holding_no_pattern_counts_as_zero():
    ctx = context('waf-regional', 'L-797E08C8')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub_pattern_sets(stub, {'bare': []})
        result = waf_check('L-797E08C8')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'bare')
        stub.assert_no_pending_responses()


def test_the_pattern_count_and_the_length_share_one_walk():
    """Both quotas read the same pattern set detail, fetched once per run."""
    ctx = context('waf-regional', 'L-D7382DD3')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub_pattern_sets(stub, {'one': ['^ab$', '^cde$']})
        assert waf_check('L-D7382DD3')(ctx)['usage'] == 2
        assert waf_check('L-797E08C8')(ctx)['usage'] == 5
        stub.assert_no_pending_responses()


def streaming_check(code):
    return next(fn for quota, _name, fn in streaming.MEDIAPACKAGE_CHECKS
                if quota == code)


def stub_v1_endpoints(stub, endpoints):
    """``endpoints`` maps an endpoint id to its startover window in seconds."""
    stub.add_response('list_channels', {'Channels': [{'Id': 'channel'}]}, {})
    stub.add_response('list_origin_endpoints', {'OriginEndpoints': [
        {'Id': identity, 'ChannelId': 'channel',
         **({} if window is None else {'StartoverWindowSeconds': window})}
        for identity, window in endpoints.items()]}, {'ChannelId': 'channel'})


def test_the_longest_time_shifted_window_is_measured():
    ctx = context('mediapackage', 'L-8D3D8B62')
    with Stubber(ctx.client('mediapackage')) as stub:
        stub_v1_endpoints(stub, {'short': 300, 'long': 86400})
        result = streaming_check('L-8D3D8B62')(ctx)
        assert (result['usage'], result['resource_id']) == (86400, 'long')
        stub.assert_no_pending_responses()


def test_an_endpoint_without_a_startover_window_counts_as_zero():
    """Time shifting is optional, so an endpoint without it shifts by nothing."""
    ctx = context('mediapackage', 'L-8D3D8B62')
    with Stubber(ctx.client('mediapackage')) as stub:
        stub_v1_endpoints(stub, {'live': None})
        result = streaming_check('L-8D3D8B62')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'live')
        stub.assert_no_pending_responses()


def media_check(code):
    return next(fn for quota, _name, fn in media_extra.MEDIAPACKAGEV2_CHECKS
                if quota == code)


def stub_v2_endpoints(stub, endpoints):
    stub.add_response('list_channel_groups', {'Items': [
        {'ChannelGroupName': 'group', 'Arn': 'arn:group', 'CreatedAt': 1,
         'ModifiedAt': 1}]}, {})
    stub.add_response('list_channels', {'Items': [
        {'ChannelName': 'channel', 'Arn': 'arn:channel', 'ChannelGroupName': 'group',
         'CreatedAt': 1, 'ModifiedAt': 1}]}, {'ChannelGroupName': 'group'})
    stub.add_response('list_origin_endpoints', {'Items': [
        {'Arn': f'arn:endpoint/{name}', 'ChannelGroupName': 'group',
         'ChannelName': 'channel', 'OriginEndpointName': name, 'ContainerType': 'TS'}
        for name in endpoints]},
        {'ChannelGroupName': 'group', 'ChannelName': 'channel'})
    for name, window in endpoints.items():
        stub.add_response('get_origin_endpoint', {
            'Arn': f'arn:endpoint/{name}', 'ChannelGroupName': 'group',
            'ChannelName': 'channel', 'OriginEndpointName': name,
            'ContainerType': 'TS', 'Segment': {}, 'CreatedAt': 1, 'ModifiedAt': 1,
            **({} if window is None else {'StartoverWindowSeconds': window})},
            {'ChannelGroupName': 'group', 'ChannelName': 'channel',
             'OriginEndpointName': name})


def test_the_v2_time_shifted_window_needs_the_endpoint_detail():
    """The V2 listing omits the window, so each endpoint is fetched."""
    ctx = context('mediapackagev2', 'L-3982B8D7')
    with Stubber(ctx.client('mediapackagev2')) as stub:
        stub_v2_endpoints(stub, {'short': 600, 'long': 172800})
        result = media_check('L-3982B8D7')(ctx)
        assert (result['usage'], result['resource_id']) == (172800, 'long')
        stub.assert_no_pending_responses()


def test_a_v2_endpoint_without_a_window_counts_as_zero():
    ctx = context('mediapackagev2', 'L-3982B8D7')
    with Stubber(ctx.client('mediapackagev2')) as stub:
        stub_v2_endpoints(stub, {'live': None})
        result = media_check('L-3982B8D7')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'live')
        stub.assert_no_pending_responses()


class FakeContext:
    """A context answering by method, for a response the SDK cannot produce."""

    def __init__(self, answers):
        self.answers = answers

    def call(self, _service, method, _key=None, **_kwargs):
        return self.answers[method]


def test_a_v1_endpoint_without_an_identity_is_reported():
    ctx = FakeContext({'list_channels': [{'Id': 'channel'}],
                       'list_origin_endpoints': [{'ChannelId': 'channel'}]})
    with pytest.raises(NoData, match='identity'):
        streaming_check('L-8D3D8B62')(ctx)
