from datetime import datetime, UTC
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.bedrock_configuration import (
    CHECKS, flow_nodes, guardrail_configuration, policy_items, profile_endpoints, version_count, versions,
)
from modules.qmchecks.bedrock import CHECKS as ORIGINAL, get_current_quotastatus_bedrock
from modules.qmcore.aws import CheckContext, NoData
from tests.iam_policy import granted_prefixes, grants

NOW = datetime(2026, 9, 11, tzinfo=UTC)
FID = 'FLOW123456'
GID = 'guardrail1'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}], account='123456789012')


def flow(version, nodes):
    return dict(id=FID, arn=f'arn:aws:bedrock:eu-central-1:123456789012:flow/{FID}',
                name='Flow', version=version, status='Prepared', createdAt=NOW,
                executionRoleArn='arn:aws:iam::123456789012:role/Flow', definition={'nodes': nodes},
                **({'updatedAt': NOW} if version == 'DRAFT' else {}))


def flow_summary(version):
    fields = ['id','arn','version','status','createdAt']
    if version == 'DRAFT':
        fields += ['name','updatedAt']
    return {k:v for k,v in flow(version, []).items() if k in fields}


def guardrail(version, **policies):
    return dict(guardrailId=GID, guardrailArn=f'arn:aws:bedrock:eu-central-1:123456789012:guardrail/{GID}',
                name='Guardrail', version=version, status='READY', createdAt=NOW, updatedAt=NOW,
                blockedInputMessaging='Blocked input', blockedOutputsMessaging='Blocked output', **policies)


def guardrail_summary(version):
    raw = guardrail(version)
    return dict(id=raw['guardrailId'], arn=raw['guardrailArn'], **{k:raw[k] for k in
                ['name','version','status','createdAt','updatedAt']})


def test_flow_maximum_includes_saved_versions_and_condition_default_branch():
    ctx = context('L-E211B5EA')
    nodes = [{'name':'one','type':'Input'}, {'name':'two','type':'Output'},
             {'name':'branch','type':'Condition','configuration':{'condition':{'conditions':[
                 {'name':'match','expression':'x == 1'}, {'name':'default'}]}}}]
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub.add_response('list_flows', {'flowSummaries':[flow_summary('DRAFT')]}, {})
        stub.add_response('list_flow_versions', {'flowVersionSummaries':[flow_summary('1')], 'nextToken':'next'}, {'flowIdentifier':FID})
        stub.add_response('list_flow_versions', {'flowVersionSummaries':[flow_summary('2')]}, {'flowIdentifier':FID,'nextToken':'next'})
        stub.add_response('get_flow', flow('DRAFT', nodes[:1]), {'flowIdentifier':FID,'includedData':'ALL_DATA'})
        stub.add_response('get_flow_version', flow('1', nodes), {'flowIdentifier':FID,'flowVersion':'1','includedData':'ALL_DATA'})
        stub.add_response('get_flow_version', flow('2', nodes[:2]), {'flowIdentifier':FID,'flowVersion':'2','includedData':'ALL_DATA'})
        result = flow_nodes(ctx)
        assert (result['usage'], result['resource_id']) == (3, FID+'/version/1')
        assert flow_nodes(ctx, node_type='Output')['usage'] == 1
        assert flow_nodes(ctx, conditions=True)['usage'] == 2
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('definition', [None, {}, {'nodes':[{'name':'loop','type':'Loop'}]}, {'nodes':[{'name':'unknown'}]}])
def test_missing_or_ambiguous_flow_configuration_is_not_zero(definition):
    ctx = Mock()
    data=flow('DRAFT', [])
    data['definition']=definition
    ctx.call.side_effect = [[{'id':FID}], [], data]
    with pytest.raises(NoData):
        flow_nodes(ctx)


def test_s3_count_requires_s3_service_configuration():
    ctx = Mock()
    ctx.call.side_effect = [[{'id':FID}], [], flow('DRAFT',[{'name':'store','type':'Storage'}])]
    with pytest.raises(NoData):
        flow_nodes(ctx, node_type='Storage')


def test_guardrail_maxima_use_each_version_and_keep_policy_content_out_of_metadata():
    ctx = context('L-85DABFD4')
    with Stubber(ctx.client('bedrock')) as stub:
        stub.add_response('list_guardrails', {'guardrails':[guardrail_summary('DRAFT')]}, {})
        stub.add_response('list_guardrails', {'guardrails':[guardrail_summary('DRAFT')], 'nextToken':'next'}, {'guardrailIdentifier':GID})
        stub.add_response('list_guardrails', {'guardrails':[guardrail_summary('1')]}, {'guardrailIdentifier':GID,'nextToken':'next'})
        stub.add_response('get_guardrail', guardrail('DRAFT'), {'guardrailIdentifier':GID,'guardrailVersion':'DRAFT'})
        stub.add_response('get_guardrail', guardrail('1', wordPolicy={'words':[{'text':'äöü'},{'text':'secret-word'}],
            'managedWordLists':[{'type':'PROFANITY'}]}, topicPolicy={'topics':[
                {'name':'topic','definition':'private-topic','examples':['example1','example2']}]},
            sensitiveInformationPolicy={'regexes':[{'name':'regex','pattern':'[a-z]+','action':'BLOCK'}]},
            automatedReasoningPolicy={'policies':['arn:policy:1','arn:policy:2']}),
            {'guardrailIdentifier':GID,'guardrailVersion':'1'})
        word = guardrail_configuration(ctx, 'wordPolicy','words')
        assert (word['usage'],word['resource_id']) == (2,GID+'/version/1')
        assert guardrail_configuration(ctx,'wordPolicy','words','text')['usage'] == 11
        assert guardrail_configuration(ctx,'topicPolicy','topics','examples')['usage'] == 2
        assert guardrail_configuration(ctx,'sensitiveInformationPolicy','regexes','pattern')['usage'] == 6
        assert guardrail_configuration(ctx,'automatedReasoningPolicy','policies')['usage'] == 2
        assert word['meta'] is None
        assert 'secret' not in repr(word)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('resource', ['Guardrail','Prompt'])
def test_version_counts_exclude_draft_and_deduplicate_published_versions(resource):
    ctx = Mock()
    ctx.call.side_effect = [[{'id':'parent1'},{'id':'parent2'}],
                            [{'id':'parent1','version':v} for v in ['DRAFT','1','1','2']],
                            [{'id':'parent2','version':'DRAFT'}]]
    result=version_count(ctx,resource)
    assert (result['usage'],result['resource_id']) == (2,'parent1')


@pytest.mark.parametrize('item', [{'id':'other','version':'1'}, {'id':'same','version':None}, {'id':'same','version':'0'}])
def test_bad_version_inventory_is_unknown(item):
    with pytest.raises(NoData):
        versions([item],'same')


def test_profile_endpoint_count_preserves_regions_and_deduplicates_identical_arns():
    ctx=Mock()
    east='arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0'
    west=east.replace('us-east-1','us-west-2')
    ctx.call.return_value=[{'inferenceProfileArn':'profile','models':[{'modelArn':v} for v in [east,west,east]]}]
    assert profile_endpoints(ctx)['usage'] == 2


def test_later_version_access_failure_does_not_emit_partial_usage():
    ctx=context('L-E211B5EA')
    with Stubber(ctx.client('bedrock-agent')) as stub:
        stub.add_response('list_flows', {'flowSummaries':[flow_summary('DRAFT')]}, {})
        stub.add_response('list_flow_versions', {'flowVersionSummaries':[flow_summary('1')]}, {'flowIdentifier':FID})
        stub.add_response('get_flow', flow('DRAFT',[{'name':'one','type':'Input'}]), {'flowIdentifier':FID,'includedData':'ALL_DATA'})
        stub.add_client_error('get_flow_version','AccessDeniedException',expected_params={
            'flowIdentifier':FID,'flowVersion':'1','includedData':'ALL_DATA'})
        row,=get_current_quotastatus_bedrock(ctx=ctx,skip={('bedrock',code) for code,_,_ in ORIGINAL})
        assert row['qualityStatus']=='ERROR'
        assert row['usageValue'] is None


def test_configuration_checks_are_unique():
    assert len(CHECKS)==len({code for code,_,_ in CHECKS})==25


def test_absent_policy_is_empty_but_incomplete_present_policy_is_unknown():
    assert policy_items({}, 'topicPolicy', 'topics') == []
    with pytest.raises(NoData):
        policy_items({'topicPolicy': {}}, 'topicPolicy', 'topics')


def test_deployed_permissions_use_iam_prefix_instead_of_sdk_client_name():
    required = {'ListFlows', 'ListFlowVersions', 'GetFlow', 'GetFlowVersion',
                'ListPrompts', 'ListGuardrails', 'GetGuardrail', 'ListInferenceProfiles',
                'ListKnowledgeBases', 'ListBlueprints'}
    ungranted = sorted(name for name in required if not grants('bedrock:' + name))
    assert not ungranted, f'bedrock operations without a grant: {ungranted}'
    # These are SDK client names, not IAM prefixes; a grant written for one
    # authorises nothing.
    assert not {'bedrock-agent', 'bedrock-data-automation'} & granted_prefixes()
