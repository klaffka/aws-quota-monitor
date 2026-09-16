"""Bedrock flow execution concurrency and the reissued batch model codes."""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import bedrock_batch, bedrock_throughput
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=timezone.utc)


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def execution(identity, status, flow='flow-1'):
    return {'executionArn': f'arn:aws:bedrock:eu-central-1:1:flow/{flow}/execution/{identity}',
            'flowIdentifier': flow, 'flowAliasIdentifier': 'alias-1', 'flowVersion': '1',
            'status': status, 'createdAt': MOMENT}


def test_only_running_flow_executions_hold_the_account_quota():
    ctx = context('L-F1613626')
    with Stubber(ctx.client('bedrock-agent')) as agent, \
            Stubber(ctx.client('bedrock-agent-runtime')) as runtime:
        agent.add_response('list_flows', {'flowSummaries': [
            {'id': 'flow-1', 'arn': 'arn:aws:bedrock:eu-central-1:1:flow/flow-1',
             'name': 'one', 'status': 'Prepared', 'createdAt': MOMENT, 'updatedAt': MOMENT,
             'version': 'DRAFT'},
            {'id': 'flow-2', 'arn': 'arn:aws:bedrock:eu-central-1:1:flow/flow-2',
             'name': 'two', 'status': 'Prepared', 'createdAt': MOMENT, 'updatedAt': MOMENT,
             'version': 'DRAFT'}]}, {})
        runtime.add_response('list_flow_executions', {'flowExecutionSummaries': [
            execution('e1', 'Running'), execution('e2', 'Succeeded'),
            execution('e3', 'Failed')]}, {'flowIdentifier': 'flow-1'})
        runtime.add_response('list_flow_executions', {'flowExecutionSummaries': [
            execution('e4', 'Running', flow='flow-2')]}, {'flowIdentifier': 'flow-2'})
        result = check('L-F1613626', bedrock_throughput.CHECKS)(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_SUM')
        agent.assert_no_pending_responses()
        runtime.assert_no_pending_responses()


def test_an_unknown_flow_execution_status_is_reported():
    ctx = context('L-F1613626')
    with Stubber(ctx.client('bedrock-agent')) as agent, \
            Stubber(ctx.client('bedrock-agent-runtime')) as runtime:
        agent.add_response('list_flows', {'flowSummaries': [
            {'id': 'flow-1', 'arn': 'arn:aws:bedrock:eu-central-1:1:flow/flow-1',
             'name': 'one', 'status': 'Prepared', 'createdAt': MOMENT, 'updatedAt': MOMENT,
             'version': 'DRAFT'}]}, {})
        runtime.add_response('list_flow_executions',
                             {'flowExecutionSummaries': [execution('e1', 'Meandering')]},
                             {'flowIdentifier': 'flow-1'})
        with pytest.raises(NoData, match='status'):
            check('L-F1613626', bedrock_throughput.CHECKS)(ctx)


REISSUED = {'L-5C48945B': 'L-91E3DBE2',   # Qwen3 235B
            'L-87CD099E': 'L-7B9A79C8',   # Qwen3 32B
            'L-FEA282F8': 'L-F30EAB98'}   # Qwen3 Coder 30B


@pytest.mark.parametrize('reissued, original', sorted(REISSUED.items()))
def test_a_reissued_code_names_the_model_its_twin_already_named(reissued, original):
    """The second export gives these models a second code, not a second model."""
    models = {code: (model, kind) for code, model, kind in bedrock_batch.MODEL_QUOTAS}
    assert models[reissued] == models[original]


def test_every_batch_model_code_appears_in_the_catalog():
    """A mapped code that no export lists would measure a quota nobody has."""
    import json
    from pathlib import Path
    catalog = json.loads(Path('tests/fixtures/quota-catalog-union.json').read_text(encoding='utf-8'))
    known = {q['QuotaCode'] for q in catalog if q.get('ServiceCode') == 'bedrock'}
    missing = sorted(code for code, _model, _kind in bedrock_batch.MODEL_QUOTAS
                     if code not in known)
    assert not missing, f'no export lists these mapped codes: {missing}'
