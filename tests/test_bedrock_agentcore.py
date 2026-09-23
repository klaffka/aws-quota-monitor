import json
from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import Mock

import boto3
import pytest
from botocore import xform_name
from botocore.stub import Stubber

from modules.qmchecks.bedrock_agentcore import (
    ACCOUNT_CHECKS, PARENT_CHECKS, CHECKS, CONTROL, SERVICE,
    active_sessions, memory_strategies, parent_count, get_current_quotastatus_bedrock_agentcore,
)
from modules.qmcore.aws import CheckContext
from modules.qmcore.registry import custom_keys


@pytest.mark.parametrize('code,name,method,key,kwargs', ACCOUNT_CHECKS)
def test_account_checks_call_real_sdk_operations_and_return_empty_inventory(code, name, method, key, kwargs):
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), [
        {'ServiceCode': SERVICE, 'QuotaCode': code, 'Value': 100}], account='123456789012')
    with Stubber(ctx.client(CONTROL)) as stub:
        stub.add_response(method, {key: []}, kwargs)
        row, = get_current_quotastatus_bedrock_agentcore(ctx=ctx)
        assert row['qualityStatus'] == 'OK'
        assert row['usageValue'] == 0
        stub.assert_no_pending_responses()


def test_parent_counts_use_maximum_across_parents_and_do_not_hide_failed_calls():
    ctx = Mock()
    ctx.call.side_effect = [[{'gatewayId': 'first'}, {'gatewayId': 'second'}], [{}, {}, {}], [{}]]
    args = ('list_gateways', 'items', 'gatewayId', 'list_gateway_targets', 'items', 'gatewayIdentifier')
    result = parent_count(ctx, *args)
    assert result['usage'] == 3
    assert result['resource_id'] == 'first'
    assert ctx.call.call_args.kwargs == {'gatewayIdentifier': 'second'}
    ctx.call.side_effect = [[{'gatewayId': 'first'}, {'gatewayId': 'second'}], [{}], RuntimeError('denied')]
    with pytest.raises(RuntimeError, match='denied'):
        parent_count(ctx, *args)


def test_memory_strategies_distinguish_sum_maximum_and_builtin_types():
    ctx = Mock()
    def call(service, method, key=None, **kwargs):
        if method == 'list_memories':
            return [{'id': 'memory-one'}, {'id': 'memory-two'}]
        assert kwargs['view'] == 'without_decryption'
        types = ['SEMANTIC', 'CUSTOM', 'SUMMARIZATION'] if kwargs['memoryId'] == 'memory-one' else ['SEMANTIC', 'SEMANTIC']
        return {'memory': {'strategies': [{'type': value} for value in types]}}
    ctx.call.side_effect = call
    assert memory_strategies(ctx)['usage'] == 3
    assert memory_strategies(ctx, total=True)['usage'] == 5
    assert memory_strategies(ctx, strategy_type='SEMANTIC')['usage'] == 2
    assert memory_strategies(ctx, strategy_type='USER_PREFERENCE')['usage'] == 0


@pytest.mark.parametrize('browser', [True, False])
def test_active_sessions_include_custom_and_system_tools_and_pagination(browser):
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), account='123456789012')
    noun = 'browser' if browser else 'codeInterpreter'
    method = 'list_browsers' if browser else 'list_code_interpreters'
    list_key = 'browserSummaries' if browser else 'codeInterpreterSummaries'
    session_method = 'list_browser_sessions' if browser else 'list_code_interpreter_sessions'
    now = datetime.now(UTC)
    def tool(identifier, status='READY'):
        return {f'{noun}Id': identifier, f'{noun}Arn': 'arn:aws:bedrock-agentcore:eu-central-1:123456789012:tool/example',
                'name': 'example', 'status': status, 'createdAt': now, 'lastUpdatedAt': now}
    def session(identifier, session_id):
        return {f'{noun}Identifier': identifier, 'sessionId': session_id, 'status': 'READY',
                'createdAt': now, 'lastUpdatedAt': now}
    with Stubber(ctx.client(CONTROL)) as control, Stubber(ctx.client(SERVICE)) as data:
        control.add_response(method, {list_key: [tool('custom-abcdefghij'), tool('deleted-abcdefghij', 'DELETED')]}, {'type': 'CUSTOM'})
        control.add_response(method, {list_key: [tool(f'aws.{noun.lower()}.v1')]}, {'type': 'SYSTEM'})
        for identifier in ('custom-abcdefghij', f'aws.{noun.lower()}.v1'):
            kwargs = {f'{noun}Identifier': identifier, 'status': 'READY'}
            data.add_response(session_method, {'items': [session(identifier, 'same-id')], 'nextToken': 'next'}, kwargs)
            data.add_response(session_method, {'items': [session(identifier, 'same-id'), session(identifier, 'other-id')]}, {**kwargs, 'nextToken': 'next'})
        assert active_sessions(ctx, browser)['usage'] == 4
        control.assert_no_pending_responses()
        data.assert_no_pending_responses()


def test_new_checks_are_registered_catalog_backed_and_match_sdk_parent_shapes():
    catalog = {q['QuotaCode'] for q in json.loads(Path('tests/fixtures/selected-service-quotas.json').read_text())
               if q['ServiceCode'] == SERVICE}
    codes = {code for code, _, _ in CHECKS}
    assert len(codes) == len(CHECKS) == 28
    assert codes <= catalog
    assert {(SERVICE, code) for code in codes} <= custom_keys()
    model = boto3.Session()._session.get_service_model(CONTROL)
    operations = {xform_name(name): model.operation_model(name) for name in model.operation_names}
    for _, _, pm, pk, identifier, cm, ck, parameter in PARENT_CHECKS:
        assert identifier in operations[pm].output_shape.members[pk].member.members
        assert parameter in operations[cm].input_shape.members
        assert ck in operations[cm].output_shape.members


def test_unknown_service_and_official_metric_skip_do_not_call_aws():
    ctx = Mock(quotas={})
    ctx.run.return_value = []
    assert get_current_quotastatus_bedrock_agentcore(ctx=ctx) == []
    ctx.run.assert_called_once_with(SERVICE, [], ())
    quota = {'ServiceCode': SERVICE, 'QuotaCode': 'L-81002DCC', 'Value': 10}
    real = CheckContext(boto3.Session(region_name='eu-central-1'), [quota], account='123456789012')
    with Stubber(real.client(CONTROL)):
        assert get_current_quotastatus_bedrock_agentcore(ctx=real, skip={(SERVICE, 'L-81002DCC')}) == []
