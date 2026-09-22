import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cloudformation as checks
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)
STACK = 'arn:aws:cloudformation:eu-central-1:123456789012:stack/example/12345678'
YAML_TEMPLATE = '''
AWSTemplateFormatVersion: '2010-09-09'
Description: Grüße
# A disabled reference is a YAML comment and does not consume the quota:
# {{resolve:ssm:/disabled-private-name}}
Parameters:
  ParameterLong:
    Type: String
Mappings:
  RegionMapping:
    eu-central-1:
      Architecture: arm64
      AMI: ami-123
    us-east-1:
      Architecture: x86_64
      AMI: ami-456
  Tiny:
    x:
      y: z
Resources:
  ResourceLogicalName:
    Type: AWS::S3::Bucket
    Properties:
      Name: !Sub '{{resolve:ssm:/private-name}}-${AWS::Region}'
  Other:
    Type: AWS::SNS::Topic
    Properties:
      Name: !Ref ParameterLong
Outputs:
  OutputLogicalName:
    Value: !GetAtt ResourceLogicalName.Arn
'''.strip()


def context(code='L-05BC894F'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'cloudformation', 'QuotaCode': code, 'Value': 500}], account='123456789012')


def stack(identity=STACK, status='CREATE_COMPLETE'):
    return {'StackId': identity, 'StackName': 'example', 'TemplateDescription': 'template',
            'CreationTime': NOW, 'StackStatus': status}


def test_processed_yaml_template_supports_intrinsic_tags_and_all_measurements_share_api_cache():
    ctx = context()
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_stacks', {'StackSummaries': [stack(), stack()], 'NextToken': 'next'}, {})
        stub.add_response('list_stacks', {'StackSummaries': [stack()]}, {'NextToken': 'next'})
        stub.add_response('get_template', {'TemplateBody': YAML_TEMPLATE, 'StagesAvailable': ['Original', 'Processed']},
                          {'StackName': STACK, 'TemplateStage': 'Processed'})
        expected = {
            'resources': 2, 'parameters': 1, 'outputs': 1, 'mappings': 2,
            'mapping_attributes': 2, 'dynamic_references': 1,
            'resource_name_length': len('ResourceLogicalName'),
            'mapping_name_length': len('RegionMapping'),
            'parameter_name_length': len('ParameterLong'),
            'output_name_length': len('OutputLogicalName'),
            'description_length': len('Grüße'.encode('utf-8')),
        }
        for measure, usage in expected.items():
            result = checks.template_measure(ctx, measure)
            assert result['usage'] == usage
            assert 'private-name' not in str(result)
        stub.assert_no_pending_responses()


def test_json_template_and_empty_optional_sections_are_supported():
    body = json.dumps({'Description': '', 'Resources': {'Bucket': {'Type': 'AWS::S3::Bucket'}}})
    ctx = Mock()
    ctx.call.side_effect = [[{'StackName': 'stack', 'StackStatus': 'CREATE_COMPLETE'}],
                            {'TemplateBody': body, 'StagesAvailable': ['Processed']}]
    assert checks.template_measure(ctx, 'resources')['usage'] == 1
    ctx.call.side_effect = None
    ctx.call.return_value = []
    assert checks.template_measure(ctx, 'outputs')['usage'] == 0


def test_template_size_uses_original_utf8_body_and_catalog_megabytes():
    body = 'Description: Grüße\nResources:\n  R:\n    Type: AWS::S3::Bucket'
    ctx = context('L-125EDA8C')
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_stacks', {'StackSummaries': [stack()]}, {})
        stub.add_response('get_template', {'TemplateBody': body,
                                            'StagesAvailable': ['Original', 'Processed']},
                          {'StackName': STACK, 'TemplateStage': 'Original'})
        result = checks.template_measure(ctx, 'template_size')
        assert result['usage'] == len(body.encode('utf-8')) / (1024 * 1024)
        assert result['unit'] == 'Megabytes'
        assert 'Grüße' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('body', [None, '', '[]', 'Resources: []', 'Resources: {}', 'Resources: ['])
def test_invalid_or_incomplete_template_is_not_zero(body):
    ctx = Mock()
    ctx.call.side_effect = [[{'StackName': 'stack', 'StackStatus': 'CREATE_COMPLETE'}],
                            {'TemplateBody': body, 'StagesAvailable': ['Processed']}]
    with pytest.raises(NoData):
        checks.template_measure(ctx, 'resources')


@pytest.mark.parametrize('template', [
    {'Resources': {'R': {}}, 'Mappings': {'Map': []}},
    {'Resources': {'R': {}}, 'Mappings': {'Map': {'row': []}}},
    {'Resources': {'R': {}}, 'Mappings': {'Map': {1: {'value': 'x'}}}},
    {'Resources': {'R': {}}, 'Mappings': {'Map': {'row': {1: 'x'}}}},
])
def test_invalid_mapping_shapes_do_not_emit_configuration_usage(template):
    with pytest.raises(NoData):
        list(checks.mapping_details(template))


def test_description_quota_uses_utf8_bytes_and_requires_literal_text():
    assert checks.parse_template('Description: Grüße\nResources:\n  R:\n    Type: AWS::S3::Bucket')['Description'] == 'Grüße'
    ctx = Mock()
    ctx.call.side_effect = [[{'StackName': 'stack', 'StackStatus': 'CREATE_COMPLETE'}],
                            {'TemplateBody': 'Description: [not, text]\nResources:\n  R: {}',
                             'StagesAvailable': ['Processed']}]
    with pytest.raises(NoData):
        checks.template_measure(ctx, 'description_length')


def test_missing_processed_stage_and_conflicting_stack_pages_are_unknown():
    ctx = Mock()
    ctx.call.side_effect = [[{'StackId': STACK, 'StackStatus': 'CREATE_COMPLETE'}],
                            {'TemplateBody': YAML_TEMPLATE, 'StagesAvailable': ['Original']}]
    with pytest.raises(NoData):
        checks.template_measure(ctx, 'resources')
    ctx.call.side_effect = None
    ctx.call.return_value = [stack(), dict(stack(), StackName='changed')]
    with pytest.raises(NoData):
        checks.template_stacks(ctx)


def test_deleted_stack_history_is_not_inspected():
    ctx = Mock()
    ctx.call.return_value = [stack(status='DELETE_COMPLETE')]
    assert checks.template_measure(ctx, 'resources')['usage'] == 0
    assert ctx.call.call_count == 1


def test_later_template_access_failure_prevents_partial_collector_sample():
    ctx = context()
    later = STACK.replace('example', 'later')
    with Stubber(ctx.client('cloudformation')) as stub:
        stub.add_response('list_stacks', {'StackSummaries': [stack(), stack(later)]}, {})
        stub.add_response('get_template', {'TemplateBody': YAML_TEMPLATE, 'StagesAvailable': ['Processed']},
                          {'StackName': STACK, 'TemplateStage': 'Processed'})
        stub.add_client_error('get_template', 'AccessDenied', expected_params={
            'StackName': later, 'TemplateStage': 'Processed'})
        row, = checks.get_current_quotastatus_cloudformation(
            ctx=ctx, skip={('cloudformation', code) for code, _, _ in checks.CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_template_checks_are_registered_with_dependency_and_permission():
    codes = {'L-05BC894F', 'L-72B9A393', 'L-87D14FB7', 'L-63D096B8', 'L-1FFB6C73',
             'L-D663BAB9', 'L-84B50260', 'L-722F1E58', 'L-3B2D14A7', 'L-38FD7965', 'L-7C7532D4'}
    codes.add('L-125EDA8C')
    assert {('cloudformation', code) for code in codes} <= custom_keys()
    root = Path(__file__).parents[1]
    assert 'PyYAML==6.0.3' in (root / 'requirements.txt').read_text()
    assert grants('cloudformation:GetTemplate')
