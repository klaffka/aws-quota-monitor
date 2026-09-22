from datetime import datetime, UTC
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cases
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

NOW = datetime(2026, 9, 12, tzinfo=UTC)
DOMAIN = 'domain-1'


def context(code='L-E52A0E46'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cases', 'QuotaCode': code, 'Value': 500}], account='123456789012')


def domain(identity=DOMAIN):
    return {'domainId': identity, 'domainArn': f'arn:aws:cases:eu-central-1:123456789012:domain/{identity}',
            'name': identity}


def field(identity, kind='SingleSelect'):
    return {'fieldId': identity, 'fieldArn': f'arn:aws:cases:eu-central-1:123456789012:domain/{DOMAIN}/field/{identity}',
            'name': identity, 'type': kind, 'namespace': 'Custom'}


def layout_content(*field_ids):
    top = [{'fieldGroup': {'fields': [{'id': field_ids[0]}]}}] if field_ids else []
    more = ([{'fieldGroup': {'name': 'Details', 'fields': [{'id': value} for value in field_ids[1:]]}}]
            if len(field_ids) > 1 else [])
    return {'basic': {'topPanel': {'sections': top}, 'moreInfo': {'sections': more}}}


def test_domain_children_use_complete_paginated_inventories_and_maximum_scope():
    ctx = context('L-C5B69356')
    second = 'domain-2'
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()], 'nextToken': 'next'}, {})
        stub.add_response('list_domains', {'domains': [domain(), domain(second)]}, {'nextToken': 'next'})
        stub.add_response('list_fields', {'fields': [field('one'), field('two', 'Text')]}, {'domainId': DOMAIN})
        stub.add_response('list_fields', {'fields': [dict(field('other'), fieldArn=field('other')['fieldArn'].replace(DOMAIN, second))]},
                          {'domainId': second})
        result = cases.domain_children(ctx, 'list_fields', 'fields', 'CasesDomain')
        assert (result['usage'], result['resource_id']) == (2, DOMAIN)
        stub.assert_no_pending_responses()


def test_field_options_include_active_and_inactive_and_only_single_select_fields():
    ctx = context()
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()]}, {})
        stub.add_response('list_fields', {'fields': [field('select'), field('text', 'Text')]}, {'domainId': DOMAIN})
        stub.add_response('list_field_options', {'options': [
            {'name': 'Open', 'value': 'open', 'active': True},
            {'name': 'Closed', 'value': 'closed', 'active': False}]}, {'domainId': DOMAIN, 'fieldId': 'select'})
        result = cases.field_options(ctx)
        assert (result['usage'], result['resource_id']) == (2, DOMAIN+'/field/select')
        assert 'Open' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('kind', [None, 'Unknown'])
def test_unknown_field_type_does_not_hide_possible_options(kind):
    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': DOMAIN}], [{'fieldId': 'field', 'type': kind}]]
    with pytest.raises(NoData):
        cases.field_options(ctx)


def test_layout_field_count_combines_both_panels_and_preserves_repeated_slots():
    ctx = context('L-5B5E62BD')
    summary = {'layoutId': 'layout-1', 'layoutArn': 'arn:layout', 'name': 'Layout'}
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()]}, {})
        stub.add_response('list_layouts', {'layouts': [summary]}, {'domainId': DOMAIN})
        stub.add_response('get_layout', dict(summary, content=layout_content('field-1', 'field-2', 'field-1')),
                          {'domainId': DOMAIN, 'layoutId': 'layout-1'})
        result = cases.fields_per_layout(ctx)
        assert (result['usage'], result['resource_id']) == (3, DOMAIN+'/layout/layout-1')
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('content', [None, {}, {'other': {}}, {'basic': {'topPanel': {'sections': None}}},
                                     {'basic': {'topPanel': {'sections': [{}]}}},
                                     {'basic': {'topPanel': {'sections': [{'fieldGroup': {}}]}}},
                                     {'basic': {'topPanel': {'sections': [{'fieldGroup': {'fields': [{}]}}]}}}])
def test_incomplete_layout_content_is_not_zero(content):
    with pytest.raises(NoData):
        cases.layout_field_count(content)


def test_deleted_or_mismatched_layout_detail_is_unknown():
    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': DOMAIN}], [{'layoutId': 'layout'}],
                            {'layoutId': 'other', 'deleted': True, 'content': layout_content()}]
    with pytest.raises(NoData):
        cases.fields_per_layout(ctx)


def test_later_layout_failure_prevents_partial_collector_result():
    ctx = context('L-5B5E62BD')
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()]}, {})
        stub.add_response('list_layouts', {'layouts': [
            {'layoutId': 'first', 'layoutArn': 'arn:first', 'name': 'First'},
            {'layoutId': 'later', 'layoutArn': 'arn:later', 'name': 'Later'}]}, {'domainId': DOMAIN})
        stub.add_response('get_layout', {'layoutId': 'first', 'layoutArn': 'arn:first', 'name': 'First',
                                         'content': layout_content('field')}, {'domainId': DOMAIN, 'layoutId': 'first'})
        stub.add_client_error('get_layout', 'AccessDeniedException', expected_params={'domainId': DOMAIN, 'layoutId': 'later'})
        row, = cases.get_current_quotastatus_cases(ctx=ctx, skip={('cases', code) for code, _, _ in cases.CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_conflicting_domains_are_rejected_and_empty_inventories_are_zero():
    ctx = Mock()
    ctx.call.return_value = [{'domainId': DOMAIN, 'name': 'one'}, {'domainId': DOMAIN, 'name': 'two'}]
    with pytest.raises(NoData):
        cases.domains(ctx)
    ctx.call.return_value = []
    for _, _, check in cases.EXTENDED_CHECKS:
        assert check(ctx)['usage'] == 0


def test_extended_checks_registered_and_permissions_present():
    assert {('cases', code) for code, _, _ in cases.EXTENDED_CHECKS} <= custom_keys()
    for action in ['ListFields', 'ListFieldOptions', 'ListLayouts', 'GetLayout']:
        # Connect Cases authorises under the cases prefix.
        assert grants(f'cases:{action}')
