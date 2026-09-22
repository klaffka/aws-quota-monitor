from datetime import datetime, timezone
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cloudformation as checks
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)
NAME = 'Example::Test::Resource'


def context(code='L-EA1018E8'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cloudformation', 'QuotaCode': code, 'Value': 100}], account='123456789012')


def summary(name=NAME, kind='RESOURCE', activated=None):
    result = {'Type': kind, 'TypeName': name, 'DefaultVersionId': '00000001', 'LastUpdated': NOW}
    if activated is not None:
        result['IsActivated'] = activated
    return result


def version(value, name=NAME, kind='RESOURCE'):
    return {'Type': kind, 'TypeName': name, 'VersionId': value, 'TimeCreated': NOW}


def test_versions_per_private_type_paginate_deduplicate_and_exclude_activated_public_types():
    ctx = context()
    public = 'Public::Test::Resource'
    params = {'Type': 'RESOURCE', 'Visibility': 'PRIVATE', 'DeprecatedStatus': 'LIVE'}
    version_params = {'Type': 'RESOURCE', 'TypeName': NAME, 'DeprecatedStatus': 'LIVE'}
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_types', {'TypeSummaries': [summary(), summary(public, activated=True)], 'NextToken': 'next'}, params)
        stub.add_response('list_types', {'TypeSummaries': [summary()]}, dict(params, NextToken='next'))
        stub.add_response('list_type_versions', {'TypeVersionSummaries': [version('00000001')], 'NextToken': 'next'}, version_params)
        stub.add_response('list_type_versions', {'TypeVersionSummaries': [version('00000001'), version('00000003')]},
                          dict(version_params, NextToken='next'))
        result = checks.versions_per_type(ctx, 'RESOURCE')
        assert (result['usage'], result['resource_id']) == (2, NAME)
        assert checks.EXTENDED_CHECKS[0][2](ctx)['usage'] == 1
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('bad', [
    {},
    {'Type': 'MODULE', 'TypeName': NAME, 'VersionId': '1'},
    {'Type': 'RESOURCE', 'TypeName': 'Other::Test::Resource', 'VersionId': '1'},
    {'Type': 'RESOURCE', 'TypeName': NAME},
])
def test_invalid_type_version_inventory_is_not_zero(bad):
    ctx = Mock()
    ctx.call.side_effect = [[{'TypeName': NAME}], [bad]]
    with pytest.raises(NoData):
        checks.versions_per_type(ctx, 'RESOURCE')


def test_registered_extension_with_empty_live_version_inventory_is_unknown():
    ctx = Mock()
    ctx.call.side_effect = [[{'TypeName': NAME}], []]
    with pytest.raises(NoData, match='no live version'):
        checks.versions_per_type(ctx, 'RESOURCE')


def test_later_version_page_failure_prevents_partial_collector_sample():
    ctx = context()
    params = {'Type': 'RESOURCE', 'Visibility': 'PRIVATE', 'DeprecatedStatus': 'LIVE'}
    version_params = {'Type': 'RESOURCE', 'TypeName': NAME, 'DeprecatedStatus': 'LIVE'}
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_types', {'TypeSummaries': [summary()]}, params)
        stub.add_response('list_type_versions', {'TypeVersionSummaries': [version('1')], 'NextToken': 'next'}, version_params)
        stub.add_client_error('list_type_versions', 'AccessDenied', expected_params=dict(version_params, NextToken='next'))
        row, = checks.get_current_quotastatus_cloudformation(
            ctx=ctx, skip={('cloudformation', code) for code, _, _ in checks.CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_empty_registries_are_zero_and_checks_are_registered_with_permission():
    ctx = Mock()
    ctx.call.return_value = []
    for _, _, check in checks.EXTENDED_CHECKS:
        assert check(ctx)['usage'] == 0
    assert {('cloudformation', code) for code, _, _ in checks.EXTENDED_CHECKS} <= custom_keys()
    assert grants('cloudformation:ListTypeVersions')
