from unittest.mock import Mock

from modules.qmchecks.bedrock import CHECKS as BEDROCK
from modules.qmchecks.rekognition import CHECKS as REKOGNITION
from modules.qmchecks.comprehend import CHECKS as COMPREHEND
from modules.qmchecks.textract import CHECKS as TEXTRACT
from modules.qmchecks.appstream import CHECKS as APPSTREAM
from modules.qmchecks.iot import CHECKS as IOT
from modules.qmchecks.pinpoint import CHECKS as PINPOINT
from modules.qmchecks.connect import CHECKS as CONNECT


def test_ai_resource_counts_use_paginated_inventories():
    ctx = Mock()
    ctx.call.side_effect = [[{'knowledgeBaseId': 'kb'}], [{'ProjectArn': 'project'}],
                            [{'EndpointArn': 'endpoint'}], [{'AdapterId': 'adapter'}]]
    assert BEDROCK[0][2](ctx)['usage'] == 1
    assert REKOGNITION[0][2](ctx)['usage'] == 1
    assert COMPREHEND[0][2](ctx)['usage'] == 1
    assert TEXTRACT[0][2](ctx)['usage'] == 1


def test_rekognition_models_per_project_uses_maximum():
    ctx = Mock()
    ctx.call.side_effect = [[{'ProjectArn': 'p1'}, {'ProjectArn': 'p2'}],
                            [{'VersionName': 'v1'}], [{'VersionName': 'v2'}, {'VersionName': 'v3'}]]
    check = next(c for c in REKOGNITION if c[0] == 'L-9CF05323')
    assert check[2](ctx)['usage'] == 2


def test_bedrock_extended_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'id': 'custom'}], [{'id': 'guardrail'}],
                            [{'id': 'imported'}], [{'id': 'profile'}],
                            [{'id': 'prompt'}], [{'blueprintArn': 'arn:blueprint'}]]
    for check in [check for check in BEDROCK if check[0] in
                  {'L-CB5B847D', 'L-0E5A840C', 'L-45B04988', 'L-40EC9882',
                   'L-B783C50B', 'L-23CF4444'}]:
        assert check[2](ctx)['usage'] == 1


def test_bedrock_automated_reasoning_policies():
    ctx = Mock()
    ctx.call.return_value = [{'policyArn': 'arn:policy'}]
    check = next(c for c in BEDROCK if c[0] == 'L-DAF06DBA')
    assert check[2](ctx)['usage'] == 1


def test_appstream_and_iot_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{'Name': 'fleet'}], [{'Name': 'stack'}], [{'Name': 'image'}],
                            [{'State': 'RUNNING'}], [{'Name': 'builder'}], [{'Name': 'block'}]]
    assert [check[2](ctx)['usage'] for check in APPSTREAM] == [1, 1, 1, 1, 1, 1]
    ctx.call.side_effect = None
    ctx.call.return_value = [{'jobTemplateArn': 'arn'}]
    # Address the check by its quota code; the list order is not a contract.
    job_templates = next(check for check in IOT if check[0] == 'L-B2C87795')
    assert job_templates[2](ctx)['usage'] == 1


def test_iot_account_resource_counts_use_paginated_list_apis():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'resource'}]
    for code in {'L-0D30EFBA', 'L-1A084077', 'L-53A90E98', 'L-4C271B57', 'L-A5B47E14'}:
        check = next(check for check in IOT if check[0] == code)
        assert check[2](ctx)['usage'] == 1


def test_pinpoint_message_templates_are_partitioned_by_type():
    ctx = Mock()
    ctx.call.return_value = {'TemplatesResponse': {'Item': [{'TemplateName': 'x'}]}}
    assert PINPOINT[3][2](ctx)['usage'] == 5
    assert ctx.call.call_count == 5


def test_connect_per_instance_counts_use_maximum_scope():
    ctx = Mock()
    def call(service, method, key=None, **kwargs):
        if method == 'list_instances':
            return [{'Id': 'i1', 'Arn': 'arn:one'}, {'Id': 'i2', 'Arn': 'arn:two'}]
        if method == 'get_service_quota':
            return {'Quota': {'ServiceCode': 'connect', 'QuotaCode': kwargs['QuotaCode'], 'Value': 100,
                             'QuotaContext': {'ContextId': kwargs['ContextId'], 'ContextScope': 'RESOURCE'}}}
        return [{'Id': 'one'}, {'Id': 'two'}] if kwargs['InstanceId'] == 'i2' else [{'Id': 'one'}]
    ctx.call.side_effect = call
    existing = {'L-22922690', 'L-19A87C94', 'L-68BBE2E8', 'L-F325A715', 'L-20CD02F7'}
    checks = [check for check in CONNECT if check[0] in existing]
    assert [check[2](ctx)['usage'] for check in checks] == [2, 2, 2, 2, 2]


def test_connect_additional_parent_scoped_resource_counts():
    ctx = Mock()
    def call(service, method, key=None, **kwargs):
        if method == 'get_service_quota':
            return {'Quota': {'ServiceCode': 'connect', 'QuotaCode': kwargs['QuotaCode'], 'Value': 100,
                             'QuotaContext': {'ContextId': kwargs['ContextId'], 'ContextScope': 'RESOURCE'}}}
        return [{'Id': 'instance-1', 'Arn': 'arn:one'}, {'Id': 'instance-2', 'Arn': 'arn:two'}]
    ctx.call.side_effect = call
    additional = {'L-D68AAAE4', 'L-9A46857E', 'L-D3E7BE26', 'L-8F812903',
                  'L-0865B754', 'L-19755C7E', 'L-B93A6612', 'L-FC6A5030'}
    checks = [check for check in CONNECT if check[0] in additional]
    assert [check[2](ctx)['usage'] for check in checks] == [2] * len(checks)
