from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks.media_extra import (
    MEDIACONNECT_CHECKS,
    ROUTER_IO_STATES,
    get_current_quotastatus_media_extra,
    outputs_per_flow,
    router_count,
)
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


def test_media_connect_counts():
    ctx = Mock(quotas={('mediaconnect', code): {} for code, _, _ in MEDIACONNECT_CHECKS},
               region='eu-central-1')

    def call(service, method, key=None, **kwargs):
        assert service == 'mediaconnect'
        if method == 'list_entitlements':
            return [{}]
        if method == 'list_flows':
            return [{'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE'},
                    {'FlowArn': 'arn:flow:two', 'Status': 'STANDBY'}]
        if method == 'describe_flow':
            return {'Flow': {'FlowArn': kwargs['FlowArn'],
                             'Status': 'ACTIVE' if kwargs['FlowArn'].endswith('one') else 'STANDBY',
                             'Outputs': ([{'OutputArn': 'arn:output:one'}]
                                         if kwargs['FlowArn'].endswith('one') else [])}}
        if method == 'list_bridges':
            return [{}]
        sizes = {'list_router_inputs': 2, 'list_router_outputs': 3,
                 'list_router_network_interfaces': 1}
        subject = method.removeprefix('list_')
        return [{'Id': f'{subject}-{index}', 'Arn': f'arn:{subject}:{index}',
                 'RegionName': 'eu-central-1', 'State': 'ACTIVE'}
                for index in range(sizes[method])]

    ctx.call.side_effect = call
    ctx.run.side_effect = lambda service, checks, skip: [
        {'quotaCode': code, 'usageValue': fn(ctx)['usage']} for code, _, fn in checks]
    assert [x['usageValue'] for x in get_current_quotastatus_media_extra(ctx=ctx)] == [1, 2, 1, 1, 2, 3, 1]


def test_outputs_per_flow_uses_maximum_and_validates_parent():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE'}],
        {'Flow': {'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE',
                  'Outputs': [{'OutputArn': 'arn:output:one'},
                              {'OutputArn': 'arn:output:two'}]}},
    ]
    result = outputs_per_flow(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:flow:one')

    ctx.call.side_effect = [
        [{'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE'}],
        {'Flow': {'FlowArn': 'arn:flow:other', 'Status': 'ACTIVE', 'Outputs': []}},
    ]
    with pytest.raises(NoData, match='missing or inconsistent'):
        outputs_per_flow(ctx)


def test_outputs_per_flow_rejects_conflicting_output_inventory():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE'}],
        {'Flow': {'FlowArn': 'arn:flow:one', 'Status': 'ACTIVE',
                  'Outputs': [{'OutputArn': 'arn:output:one', 'Name': 'first'},
                              {'OutputArn': 'arn:output:one', 'Name': 'changed'}]}},
    ]
    with pytest.raises(NoData, match='changed during pagination'):
        outputs_per_flow(ctx)


def test_router_count_filters_region_and_deduplicates_identical_pages():
    item = {'Id': 'input-one', 'Arn': 'arn:input:one',
            'RegionName': 'eu-central-1', 'State': 'STANDBY'}
    ctx = Mock(region='eu-central-1')
    ctx.call.return_value = [item, dict(item),
                             dict(item, Id='other', Arn='arn:input:other',
                                  RegionName='eu-west-1')]
    result = router_count(ctx, 'list_router_inputs', 'RouterInputs', ROUTER_IO_STATES)
    assert result['usage'] == 1


@pytest.mark.parametrize('change,match', [
    ({'RegionName': None}, 'missing its Region'),
    ({'State': 'FUTURE'}, 'unknown state'),
])
def test_router_count_rejects_incomplete_inventory(change, match):
    ctx = Mock(region='eu-central-1')
    ctx.call.return_value = [dict(
        {'Id': 'input-one', 'Arn': 'arn:input:one',
         'RegionName': 'eu-central-1', 'State': 'ACTIVE'}, **change)]
    with pytest.raises(NoData, match=match):
        router_count(ctx, 'list_router_inputs', 'RouterInputs', ROUTER_IO_STATES)


def test_media_connect_checks_are_registered_with_read_permissions():
    current_codes = {'L-F1F62F5D', 'L-A99016A8', 'L-CB77E87E',
                     'L-77138741', 'L-58DF4801', 'L-6C50CD26'}
    assert {('mediaconnect', code) for code in current_codes} <= custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('DescribeFlow', 'ListRouterInputs', 'ListRouterOutputs',
                   'ListRouterNetworkInterfaces'):
        assert f'"mediaconnect:{action}"' in policy


def test_media_package_v2_parent_scoped_counts():
    from modules.qmchecks.media_extra import max_channels_per_group, max_endpoints_per_channel
    ctx = Mock()
    ctx.call.return_value = [{'ChannelGroupName': 'g1'}]
    # The group contains two channels.
    ctx.call.side_effect = [[{'ChannelGroupName': 'g1'}], [{}, {}]]
    assert max_channels_per_group(ctx)['usage'] == 2
    # The same group has one channel with three endpoints.
    ctx.call.side_effect = [[{'ChannelGroupName': 'g1'}], [{'ChannelName': 'c1'}], [{}, {}, {}]]
    assert max_endpoints_per_channel(ctx)['usage'] == 3
