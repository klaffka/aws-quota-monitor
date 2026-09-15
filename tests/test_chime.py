import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import chime
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

ACCOUNT = '123456789012'
APP = f'arn:aws:chime:eu-central-1:{ACCOUNT}:app-instance/one'
OTHER_APP = f'arn:aws:chime:eu-central-1:{ACCOUNT}:app-instance/two'
USER = f'{APP}/user/alice'
OTHER_USER = f'{APP}/user/bob'
FLOW = f'{APP}/channel-flow/moderation'
PIPELINE = '11111111-1111-1111-1111-111111111111'
OTHER_PIPELINE = '22222222-2222-2222-2222-222222222222'


def context(code='L-0222B40A'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'chime', 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(code):
    return next(fn for quota, _, fn in chime.CHECKS if quota == code)


def app_instances(stub, *arns):
    stub.add_response('list_app_instances', {'AppInstances': [
        {'AppInstanceArn': arn, 'Name': arn.rsplit('/', 1)[-1]} for arn in arns]}, {})


def test_app_instances_are_counted_once_across_pages():
    ctx = context('L-0222B40A')
    with Stubber(ctx.client('chime-sdk-identity')) as stub:
        stub.add_response('list_app_instances', {'AppInstances': [
            {'AppInstanceArn': APP}], 'NextToken': 'next'}, {})
        stub.add_response('list_app_instances', {'AppInstances': [
            {'AppInstanceArn': APP}, {'AppInstanceArn': OTHER_APP}]},
            {'NextToken': 'next'})
        assert check('L-0222B40A')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_app_instance_without_an_arn_raises_nodata():
    ctx = context('L-0222B40A')
    with Stubber(ctx.client('chime-sdk-identity')) as stub:
        stub.add_response('list_app_instances', {'AppInstances': [{'Name': 'x'}]}, {})
        with pytest.raises(NoData, match='missing its ARN'):
            check('L-0222B40A')(ctx)


def test_users_and_admins_report_the_largest_app_instance():
    ctx = context('L-D54E9933')
    with Stubber(ctx.client('chime-sdk-identity')) as stub:
        app_instances(stub, APP, OTHER_APP)
        stub.add_response('list_app_instance_users', {'AppInstanceUsers': [
            {'AppInstanceUserArn': USER}]}, {'AppInstanceArn': APP})
        stub.add_response('list_app_instance_users', {'AppInstanceUsers': [
            {'AppInstanceUserArn': f'{OTHER_APP}/user/a'},
            {'AppInstanceUserArn': f'{OTHER_APP}/user/b'}]}, {'AppInstanceArn': OTHER_APP})
        result = chime.users_per_app_instance(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_APP)
        stub.assert_no_pending_responses()


def test_admins_are_counted_per_app_instance():
    ctx = context('L-9A7ECB60')
    with Stubber(ctx.client('chime-sdk-identity')) as stub:
        app_instances(stub, APP)
        stub.add_response('list_app_instance_admins', {'AppInstanceAdmins': [
            {'Admin': {'Arn': USER, 'Name': 'alice'}}]}, {'AppInstanceArn': APP})
        result = check('L-9A7ECB60')(ctx)
        assert (result['usage'], result['resource_id']) == (1, APP)
        stub.assert_no_pending_responses()


def test_endpoints_are_counted_per_user_across_app_instances():
    ctx = context('L-39BCA56C')
    with Stubber(ctx.client('chime-sdk-identity')) as stub:
        app_instances(stub, APP)
        stub.add_response('list_app_instance_users', {'AppInstanceUsers': [
            {'AppInstanceUserArn': USER}, {'AppInstanceUserArn': OTHER_USER}]},
            {'AppInstanceArn': APP})
        stub.add_response('list_app_instance_user_endpoints', {
            'AppInstanceUserEndpoints': [{'AppInstanceUserArn': USER, 'EndpointId': 'e1'}]},
            {'AppInstanceUserArn': USER})
        stub.add_response('list_app_instance_user_endpoints', {
            'AppInstanceUserEndpoints': [
                {'AppInstanceUserArn': OTHER_USER, 'EndpointId': 'e2'},
                {'AppInstanceUserArn': OTHER_USER, 'EndpointId': 'e3'}]},
            {'AppInstanceUserArn': OTHER_USER})
        result = chime.endpoints_per_user(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_USER)
        stub.assert_no_pending_responses()


def test_channel_flow_processors_come_from_the_summary():
    ctx = context('L-CA0C986A')
    identity = ctx.client('chime-sdk-identity')
    messaging = ctx.client('chime-sdk-messaging')
    with Stubber(identity) as id_stub, Stubber(messaging) as msg_stub:
        app_instances(id_stub, APP)
        msg_stub.add_response('list_channel_flows', {'ChannelFlows': [
            {'ChannelFlowArn': FLOW, 'Name': 'moderation', 'Processors': [
                {'Name': 'p1', 'Configuration': {'Lambda': {
                    'ResourceArn': 'arn:aws:lambda:eu-central-1:123456789012:function:a',
                    'InvocationType': 'ASYNC'}},
                 'ExecutionOrder': 1, 'FallbackAction': 'CONTINUE'}]}]},
            {'AppInstanceArn': APP})
        result = chime.processors_per_channel_flow(ctx)
        assert (result['usage'], result['resource_id']) == (1, FLOW)
        id_stub.assert_no_pending_responses()
        msg_stub.assert_no_pending_responses()


def test_sip_rule_targets_are_counted_per_rule():
    ctx = context('L-8BA4EAA6')
    with Stubber(ctx.client('chime-sdk-voice')) as stub:
        stub.add_response('list_sip_rules', {'SipRules': [
            {'SipRuleId': 'rule-1', 'Name': 'one', 'TargetApplications': [
                {'SipMediaApplicationId': 'app-1', 'Priority': 1},
                {'SipMediaApplicationId': 'app-2', 'Priority': 2}]},
            {'SipRuleId': 'rule-2', 'Name': 'two', 'TargetApplications': [
                {'SipMediaApplicationId': 'app-1', 'Priority': 1}]}]}, {})
        result = chime.applications_per_sip_rule(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'rule-1')
        stub.assert_no_pending_responses()


def test_a_sip_rule_without_targets_raises_nodata():
    ctx = context('L-8BA4EAA6')
    with Stubber(ctx.client('chime-sdk-voice')) as stub:
        stub.add_response('list_sip_rules', {'SipRules': [
            {'SipRuleId': 'rule-1', 'Name': 'one'}]}, {})
        with pytest.raises(NoData, match='no target applications'):
            chime.applications_per_sip_rule(ctx)


def test_account_inventories_are_counted_directly():
    for code, method, key, client in (
            ('L-8EE806B4', 'list_voice_connectors', 'VoiceConnectors', 'chime-sdk-voice'),
            ('L-9DD490AB', 'list_sip_media_applications', 'SipMediaApplications',
             'chime-sdk-voice'),
            ('L-83E6B280', 'list_media_pipeline_kinesis_video_stream_pools',
             'KinesisVideoStreamPools', 'chime-sdk-media-pipelines'),
            ('L-668D1758', 'list_media_insights_pipeline_configurations',
             'MediaInsightsPipelineConfigurations', 'chime-sdk-media-pipelines')):
        ctx = context(code)
        with Stubber(ctx.client(client)) as stub:
            stub.add_response(method, {key: [{}, {}]}, {})
            assert check(code)(ctx)['usage'] == 2, code
            stub.assert_no_pending_responses()


def test_call_analytics_pipelines_exclude_other_pipeline_kinds():
    ctx = context('L-DA073F3A')
    with Stubber(ctx.client('chime-sdk-media-pipelines')) as stub:
        stub.add_response('list_media_pipelines', {'MediaPipelines': [
            {'MediaPipelineId': PIPELINE}, {'MediaPipelineId': OTHER_PIPELINE}]}, {})
        stub.add_response('get_media_pipeline', {'MediaPipeline': {
            'MediaInsightsPipeline': {'MediaPipelineId': PIPELINE}}},
            {'MediaPipelineId': PIPELINE})
        stub.add_response('get_media_pipeline', {'MediaPipeline': {
            'MediaCapturePipeline': {'MediaPipelineId': OTHER_PIPELINE}}},
            {'MediaPipelineId': OTHER_PIPELINE})
        assert chime.call_analytics_pipelines(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_a_pipeline_without_detail_raises_nodata():
    ctx = context('L-DA073F3A')
    with Stubber(ctx.client('chime-sdk-media-pipelines')) as stub:
        stub.add_response('list_media_pipelines', {'MediaPipelines': [
            {'MediaPipelineId': PIPELINE}]}, {})
        stub.add_response('get_media_pipeline', {}, {'MediaPipelineId': PIPELINE})
        with pytest.raises(NoData, match='no detail'):
            chime.call_analytics_pipelines(ctx)


def test_every_chime_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'chime'}
    assert {code for code, _, _ in chime.CHECKS} <= registered
