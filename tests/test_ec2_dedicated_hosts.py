import json
import re
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.ec2.ec2 import dedicated_hosts, get_current_quotastatus_ec2, CHECKS
from modules.qmchecks.ec2.host_families import HOST_FAMILIES
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '123456789012'


def host(identity='h-one', family='m5', **fields):
    return dict(HostId=identity, OwnerId=ACCOUNT, State='available',
                HostProperties={'InstanceFamily': family}, **fields)


def test_hosts_paginate_cache_and_count_families_without_guest_counts():
    session = boto3.Session(region_name='eu-central-1')
    ctx = CheckContext(session, account=ACCOUNT)
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_hosts', {'Hosts': [host(), host('h-two', 'c5')],
                                            'NextToken': 'page-two'}, {})
        single_size = host('h-three')
        single_size['HostProperties'] = {'InstanceType': 'm5.large'}
        released = host('h-released')
        released['State'] = 'released'
        shared = host('h-shared')
        shared['OwnerId'] = '999999999999'
        stub.add_response('describe_hosts', {'Hosts': [single_size, released, shared, host()]},
                          {'NextToken': 'page-two'})
        assert dedicated_hosts(ctx, 'm5')['usage'] == 2
        assert dedicated_hosts(ctx, 'c5')['usage'] == 1
        assert dedicated_hosts(ctx, 'u-6tb1')['usage'] == 0
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('fields', [
    {'State': 'pending'}, {'State': 'under-assessment'}, {'State': 'permanent-failure'},
    {'State': 'configuring'}, {'State': 'unknown'}, {'State': None},
    {'OwnerId': None}, {'HostProperties': {}}, {'HostId': None},
    {'OutpostArn': 'arn:aws:outposts:eu-central-1:123456789012:outpost/op-one'},
])
def test_ambiguous_host_inventory_does_not_become_zero(fields):
    item = host()
    item.update(fields)
    ctx = Mock(account=ACCOUNT)
    ctx.call.return_value = [item]
    with pytest.raises(NoData):
        dedicated_hosts(ctx, 'm5')


def test_failure_on_later_inventory_page_returns_error_without_partial_usage():
    code = next(code for code, family in HOST_FAMILIES.items() if family == 'm5')
    quota = {'ServiceCode': 'ec2', 'QuotaCode': code, 'Value': 5}
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), [quota], account=ACCOUNT)
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_hosts', {'Hosts': [host()], 'NextToken': 'page-two'}, {})
        stub.add_client_error('describe_hosts', service_error_code='UnauthorizedOperation',
                              expected_params={'NextToken': 'page-two'})
        rows = get_current_quotastatus_ec2(ctx=ctx, skip={('ec2', c) for c, _, _ in CHECKS})
        assert len(rows) == 1
        assert rows[0]['qualityStatus'] == 'ERROR'
        assert rows[0]['usageValue'] is None
        stub.assert_no_pending_responses()


def test_collector_selects_only_catalog_families_and_honors_official_metrics():
    quota = {'ServiceCode': 'ec2', 'QuotaCode': 'L-81657574', 'Value': 5}
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), [quota], account=ACCOUNT)
    skip = {('ec2', c) for c, _, _ in CHECKS}
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_hosts', {'Hosts': [host(family='c5')]}, {})
        rows = get_current_quotastatus_ec2(ctx=ctx, skip=skip)
        assert [(r['quotaCode'], r['usageValue'], r['qualityStatus']) for r in rows] == [
            ('L-81657574', 1, 'OK')]
        stub.assert_no_pending_responses()
    assert get_current_quotastatus_ec2(ctx=ctx, skip=skip | {('ec2', 'L-81657574')}) == []


def test_family_mapping_matches_every_dedicated_host_quota_in_current_catalog():
    catalog = json.loads(Path('tests/fixtures/selected-service-quotas.json').read_text())
    expected = {}
    for quota in catalog:
        match = re.fullmatch(r'Running Dedicated ([a-z0-9-]+) Hosts', quota['QuotaName'])
        if quota['ServiceCode'] == 'ec2' and match:
            expected[quota['QuotaCode']] = match[1]
    assert expected == HOST_FAMILIES
    assert {('ec2', code) for code in expected} <= custom_keys()
