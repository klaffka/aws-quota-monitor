from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cases
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys


NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)
DOMAIN = 'domain-1'


def context(code='L-C1AF8D37'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cases', 'QuotaCode': code, 'Value': 500}],
                        account='123456789012')


def domain():
    return {'domainId': DOMAIN,
            'domainArn': f'arn:aws:cases:eu-central-1:123456789012:domain/{DOMAIN}',
            'name': DOMAIN}


def related(identity, case_id, kind, content):
    return {'relatedItemId': identity, 'caseId': case_id, 'type': kind,
            'associationTime': NOW, 'content': content}


def test_related_item_quotas_use_one_complete_domain_inventory():
    file_one = related('file-1', 'case-1', 'File', {'file': {'fileArn': 'arn:file:1'}})
    file_two = related('file-2', 'case-1', 'File', {'file': {'fileArn': 'arn:file:2'}})
    sla = related('sla-1', 'case-1', 'Sla', {'sla': {'slaConfiguration': {
        'name': 'response', 'type': 'CaseField', 'status': 'Active', 'targetTime': NOW}}})
    custom = related('custom-1', 'case-1', 'Custom', {'custom': {'fields': [
        {'id': 'field-1', 'value': {'stringValue': 'private'}},
        {'id': 'field-2', 'value': {'doubleValue': 2}},
        {'id': 'field-3', 'value': {'booleanValue': True}},
    ]}})
    other = related('file-3', 'case-2', 'File', {'file': {'fileArn': 'arn:file:3'}})
    ctx = context()
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()]}, {})
        stub.add_response('search_all_related_items',
                          {'relatedItems': [file_one, file_two, sla, custom], 'nextToken': 'next'},
                          {'domainId': DOMAIN})
        stub.add_response('search_all_related_items', {'relatedItems': [file_one, other]},
                          {'domainId': DOMAIN, 'nextToken': 'next'})
        expected = {'related_items': 4, 'files': 2, 'slas': 1, 'custom_fields': 3}
        for measure, usage in expected.items():
            result = cases.related_item_measure(ctx, measure)
            assert result['usage'] == usage
            assert 'private' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('item', [
    {'caseId': 'case', 'relatedItemId': 'item', 'type': 'Future', 'content': {'future': {}}},
    {'caseId': 'case', 'relatedItemId': 'item', 'type': 'File', 'content': {'comment': {}}},
    {'caseId': 'case', 'relatedItemId': 'item', 'type': 'File', 'content': {'file': {}, 'comment': {}}},
])
def test_related_item_unknown_or_mismatched_union_is_not_counted(item):
    ctx = Mock()
    ctx.call.return_value = [item]
    with pytest.raises(NoData):
        cases.related_items(ctx, DOMAIN)


def test_conflicting_related_item_pages_are_rejected():
    first = related('item', 'case', 'File', {'file': {'fileArn': 'arn:first'}})
    ctx = Mock()
    ctx.call.return_value = [first, dict(first, content={'file': {'fileArn': 'arn:changed'}})]
    with pytest.raises(NoData):
        cases.related_items(ctx, DOMAIN)


@pytest.mark.parametrize('fields', [None, [{}], [{'id': 'field', 'value': {}}],
                                                 [{'id': 'field', 'value': {'a': 1, 'b': 2}}]])
def test_custom_related_item_requires_complete_field_values(fields):
    item = related('custom', 'case', 'Custom', {'custom': {'fields': fields}})
    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': DOMAIN}], [item]]
    with pytest.raises(NoData):
        cases.related_item_measure(ctx, 'custom_fields')


def rule_summary(identity, kind):
    return {'caseRuleId': identity, 'name': identity, 'caseRuleArn': f'arn:rule:{identity}',
            'ruleType': kind}


def rule_detail(identity, rule):
    return {'caseRuleId': identity, 'name': identity, 'caseRuleArn': f'arn:rule:{identity}',
            'rule': rule}


def test_field_option_rule_and_template_quotas_share_validated_rule_inventory():
    field_options = rule_summary('field-options', 'FieldOptions')
    required = rule_summary('required', 'Required')
    mappings = [
        {'parentFieldOptionValue': 'a', 'childFieldOptionValues': ['one', 'two']},
        {'parentFieldOptionValue': 'b', 'childFieldOptionValues': ['three']},
    ]
    template = {'templateId': 'template-1', 'templateArn': 'arn:template:1',
                'name': 'template', 'status': 'Active'}
    ctx = context('L-F43DCB55')
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain()]}, {})
        stub.add_response('list_case_rules', {'caseRules': [field_options, required]},
                          {'domainId': DOMAIN})
        stub.add_response('batch_get_case_rule', {'caseRules': [
            rule_detail('field-options', {'fieldOptions': {
                'parentFieldId': 'parent', 'childFieldId': 'child',
                'parentChildFieldOptionsMappings': mappings}}),
            rule_detail('required', {'required': {'defaultValue': True, 'conditions': []}}),
        ], 'errors': []}, {'domainId': DOMAIN,
                           'caseRules': [{'id': 'field-options'}, {'id': 'required'}]})
        assert cases.field_option_rule_measure(ctx, 'parent_values')['usage'] == 2
        assert cases.field_option_rule_measure(ctx, 'child_values')['usage'] == 3
        stub.add_response('list_templates', {'templates': [template]}, {'domainId': DOMAIN})
        stub.add_response('get_template', dict(template, rules=[
            {'caseRuleId': 'field-options', 'fieldId': 'child'},
            {'caseRuleId': 'required', 'fieldId': 'title'},
        ]), {'domainId': DOMAIN, 'templateId': 'template-1'})
        assert cases.field_option_rules_per_template(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('response', [
    {'caseRules': [], 'errors': [{'id': 'rule', 'errorCode': 'AccessDenied'}]},
    {'caseRules': [], 'errors': [], 'unprocessedCaseRules': ['rule']},
    {'caseRules': [], 'errors': []},
])
def test_incomplete_case_rule_batch_is_unknown(response):
    ctx = Mock()
    ctx.call.side_effect = [[rule_summary('rule', 'FieldOptions')], response]
    with pytest.raises(NoData):
        cases.case_rule_details(ctx, DOMAIN)


def test_rule_detail_type_and_template_references_must_match_inventory():
    ctx = Mock()
    ctx.call.side_effect = [
        [rule_summary('rule', 'FieldOptions')],
        {'caseRules': [rule_detail('rule', {'required': {'defaultValue': True, 'conditions': []}})],
         'errors': []},
    ]
    with pytest.raises(NoData):
        cases.case_rule_details(ctx, DOMAIN)

    ctx = Mock()
    ctx.call.side_effect = [[{'domainId': DOMAIN}], {}, [{'templateId': 'template'}],
                            {'templateId': 'template', 'rules': [{'caseRuleId': 'missing'}]}]
    with pytest.raises(NoData):
        cases.field_option_rules_per_template(ctx)


def test_later_related_item_failure_prevents_partial_collector_sample():
    ctx = context('L-C1AF8D37')
    second = 'domain-2'
    second_domain = dict(domain(), domainId=second,
                         domainArn=domain()['domainArn'].replace(DOMAIN, second), name=second)
    with Stubber(ctx.client('connectcases')) as stub:
        stub.add_response('list_domains', {'domains': [domain(), second_domain]}, {})
        stub.add_response('search_all_related_items', {'relatedItems': [
            related('item', 'case', 'File', {'file': {'fileArn': 'arn:file'}})]},
            {'domainId': DOMAIN})
        stub.add_client_error('search_all_related_items', 'AccessDeniedException',
                              expected_params={'domainId': second})
        row, = cases.get_current_quotastatus_cases(
            ctx=ctx, skip={('cases', code) for code, _, _ in cases.CHECKS})
        assert row['qualityStatus'] == 'ERROR' and row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_remaining_content_quota_checks_are_registered_with_permissions():
    codes = {'L-C1AF8D37', 'L-930905B5', 'L-A7158118', 'L-7D21A319',
             'L-F43DCB55', 'L-435DBDE3', 'L-8F7DFC0D'}
    assert {('cases', code) for code in codes} <= custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text()
    for action in ('SearchAllRelatedItems', 'BatchGetCaseRule', 'GetTemplate'):
        assert f'"connectcases:{action}"' in policy
