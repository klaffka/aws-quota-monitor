from datetime import datetime, UTC
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.cleanrooms_ml import (
    CHECKS, active_versions, audience_jobs, get_current_quotastatus_cleanrooms_ml,
    inference_jobs, membership_inventory, model_versions, training_instances, training_jobs,
)
from modules.qmchecks.cleanrooms_ml_quotas import TRAINING_INSTANCE_QUOTAS
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 11, tzinfo=UTC)
MID = '11111111-1111-1111-1111-111111111111'
CID = '22222222-2222-2222-2222-222222222222'
VERSIONS = ['00000000-0000-0000-0000-00000000000' + str(i) for i in range(1, 4)]
ARN = f'arn:aws:cleanrooms-ml:eu-central-1:123456789012:membership/{MID}/trained-model/model'
ASSOC = f'arn:aws:cleanrooms-ml:eu-central-1:123456789012:membership/{MID}/configured-model-algorithm-association/algorithm'
TYPE = 'ml.m5.2xlarge'


def context(codes=('L-FF7AD06D',)):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode':'cleanrooms-ml','QuotaCode':code,'Value':10} for code in codes],
                        account='123456789012')


def membership():
    return dict(id=MID, arn=f'arn:aws:cleanrooms:eu-central-1:123456789012:membership/{MID}',
                collaborationArn=f'arn:aws:cleanrooms:eu-central-1:123456789012:collaboration/{CID}',
                collaborationId=CID, collaborationCreatorAccountId='123456789012',
                collaborationCreatorDisplayName='Owner', collaborationName='Collaboration',
                createTime=NOW, updateTime=NOW, status='ACTIVE', memberAbilities=['CAN_QUERY'],
                paymentConfiguration={'queryCompute':{'isResponsible':True}})


def model(version=VERSIONS[0], status='CREATE_IN_PROGRESS'):
    return dict(createTime=NOW, updateTime=NOW, trainedModelArn=ARN, name='model',
                membershipIdentifier=MID, collaborationIdentifier=CID, status=status,
                configuredModelAlgorithmAssociationArn=ASSOC,
                **({'versionIdentifier':version} if version else {}))


def detail(item, count=3, kind=TYPE):
    return {**item, 'dataChannels':[{'channelName':'channel',
             'mlInputChannelArn':f'arn:aws:cleanrooms-ml:eu-central-1:123456789012:membership/{MID}/ml-input-channel/channel'}],
            'resourceConfig':{'instanceCount':count,'instanceType':kind,'volumeSizeInGB':10}}


def mocked_model_ctx(items, details=None, root=None):
    ctx=Mock()
    root = root or items[-1]
    def call(service, method, key=None, **kwargs):
        if method=='list_memberships':return [{'id':MID}]
        if method=='list_trained_models':return [root]
        if method=='list_trained_model_versions':return items
        if method=='get_trained_model':
            version=kwargs.get('versionIdentifier')
            return details[version] if details is not None else detail(next(item for item in items if item.get('versionIdentifier')==version))
        raise AssertionError(method)
    ctx.call.side_effect=call
    return ctx


def test_all_versions_count_distributed_instances_and_share_cached_paginated_inventory():
    ctx=context()
    saved=model(VERSIONS[0], 'ACTIVE')
    one,two=model(VERSIONS[1]),model(VERSIONS[2])
    with Stubber(ctx.client('cleanrooms')) as rooms, Stubber(ctx.client('cleanroomsml')) as ml:
        rooms.add_response('list_memberships', {'membershipSummaries':[membership()]}, {})
        ml.add_response('list_trained_models', {'trainedModels':[two]}, {'membershipIdentifier':MID})
        ml.add_response('list_trained_model_versions', {'trainedModels':[saved,one],'nextToken':'next'},
                        {'membershipIdentifier':MID,'trainedModelArn':ARN})
        ml.add_response('list_trained_model_versions', {'trainedModels':[one,two]},
                        {'membershipIdentifier':MID,'trainedModelArn':ARN,'nextToken':'next'})
        ml.add_response('get_trained_model', detail(one,3),
                        {'membershipIdentifier':MID,'trainedModelArn':ARN,'versionIdentifier':VERSIONS[1]})
        ml.add_response('get_trained_model', detail(two,2,'ml.m5.4xlarge'),
                        {'membershipIdentifier':MID,'trainedModelArn':ARN,'versionIdentifier':VERSIONS[2]})
        assert training_instances(ctx,TYPE)['usage']==3
        assert training_instances(ctx)['usage']==5
        assert training_instances(ctx,'ml.m5.4xlarge')['usage']==2
        assert training_jobs(ctx)['usage']==2
        assert training_jobs(ctx,per_membership=True)['usage']==2
        assert active_versions(ctx)['usage']==3
        ml.assert_no_pending_responses()
        rooms.assert_no_pending_responses()


@pytest.mark.parametrize('state', ['CREATE_PENDING','CANCEL_PENDING','CANCEL_IN_PROGRESS','CANCEL_FAILED',
                                  'DELETE_PENDING','DELETE_IN_PROGRESS','DELETE_FAILED','UNKNOWN'])
def test_ambiguous_instance_reservations_never_return_zero(state):
    with pytest.raises(NoData):
        training_instances(mocked_model_ctx([model(status=state)]),TYPE)


@pytest.mark.parametrize('count', [None,0,True,-1,1.5])
def test_missing_or_invalid_instance_counts_are_unknown(count):
    item=model()
    with pytest.raises(NoData):
        training_instances(mocked_model_ctx([item],{VERSIONS[0]:detail(item,count)}),TYPE)


def test_pending_jobs_count_as_jobs_but_have_unknown_instance_reservation():
    item=model(status='CREATE_PENDING')
    ctx=mocked_model_ctx([item])
    assert training_jobs(ctx)['usage']==1
    with pytest.raises(NoData):training_instances(ctx,TYPE)


def test_completed_artifacts_do_not_require_compute_details():
    items=[model(VERSIONS[0],'ACTIVE'),model(VERSIONS[1],'CREATE_FAILED'),model(VERSIONS[2],'INACTIVE')]
    ctx=mocked_model_ctx(items,details={})
    assert training_instances(ctx,TYPE)['usage']==0
    assert training_jobs(ctx)['usage']==0
    assert active_versions(ctx)['usage']==1


@pytest.mark.parametrize('items,root', [
    ([],model()),
    ([model(VERSIONS[0])],model(VERSIONS[1])),
    ([{**model(),'membershipIdentifier':CID}],model()),
    ([model(),model(status='ACTIVE')],model()),
])
def test_incomplete_or_inconsistent_versions_are_not_partial_counts(items,root):
    ctx=mocked_model_ctx(items,root=root)
    with pytest.raises(NoData):list(model_versions(ctx))


def test_detail_identity_and_status_must_match_selected_version():
    item=model()
    changed={**detail(item),'status':'ACTIVE'}
    with pytest.raises(NoData):
        training_instances(mocked_model_ctx([item],{VERSIONS[0]:changed}),TYPE)


def test_legacy_versionless_model_is_read_without_version_parameter():
    item=model(version=None)
    ctx=mocked_model_ctx([item])
    assert training_instances(ctx,TYPE)['usage']==3
    assert 'versionIdentifier' not in ctx.call.call_args.kwargs


def test_inference_counts_sum_memberships_while_membership_quota_takes_maximum():
    ctx=Mock()
    def call(service,method,key=None,**kwargs):
        if method=='list_memberships':return [{'id':MID},{'id':CID}]
        mid=kwargs['membershipIdentifier']
        return [{'membershipIdentifier':mid,'trainedModelInferenceJobArn':f'{mid}/{i}','status':'CREATE_IN_PROGRESS'}
                for i in range(2 if mid==MID else 3)]
    ctx.call.side_effect=call
    assert inference_jobs(ctx)['usage']==5
    assert inference_jobs(ctx,per_membership=True)['usage']==3


def test_export_jobs_sharing_generation_are_not_collapsed():
    ctx=Mock()
    ctx.call.return_value=[{'audienceGenerationJobArn':'generation','name':name,'status':'CREATE_PENDING'}
                           for name in ['export1','export2']]
    assert audience_jobs(ctx,'list_audience_export_jobs','audienceExportJobs',
                         ('audienceGenerationJobArn','name'))['usage']==2


def test_active_input_channels_exclude_pending_and_retired_channels():
    ctx=Mock()
    ctx.call.side_effect=[[{'id':MID}], [
        {'membershipIdentifier':MID,'mlInputChannelArn':str(i),'status':state}
        for i,state in enumerate(['ACTIVE','CREATE_PENDING','INACTIVE'])]]
    result=membership_inventory(ctx,'list_ml_input_channels','mlInputChannelsList','mlInputChannelArn',active=True)
    assert result['usage']==1


def test_later_api_failure_produces_error_without_usage():
    ctx=context()
    with Stubber(ctx.client('cleanrooms')) as rooms, Stubber(ctx.client('cleanroomsml')) as ml:
        rooms.add_response('list_memberships',{'membershipSummaries':[membership()]},{})
        ml.add_response('list_trained_models',{'trainedModels':[model()]},{'membershipIdentifier':MID})
        ml.add_client_error('list_trained_model_versions','AccessDeniedException',expected_params={
            'membershipIdentifier':MID,'trainedModelArn':ARN})
        row,=get_current_quotastatus_cleanrooms_ml(ctx=ctx)
        assert row['qualityStatus']=='ERROR'
        assert row['usageValue'] is None


def test_empty_account_is_zero_usage_but_zero_applied_limit_has_no_percentage():
    ctx=context()
    ctx.quotas[('cleanrooms-ml','L-FF7AD06D')]['Value']=0
    with Stubber(ctx.client('cleanrooms')) as stub:
        stub.add_response('list_memberships',{'membershipSummaries':[]},{})
        row,=get_current_quotastatus_cleanrooms_ml(ctx=ctx)
        assert row['usageValue']==0
        assert row['qualityStatus']=='NO_DATA'
        assert row['utilizationPct'] is None


def test_all_reviewed_instance_types_are_supported_and_registered():
    sdk=context().client('cleanroomsml').meta.service_model
    supported=set(sdk.shape_for('ResourceConfig').members['instanceType'].enum)
    assert len(TRAINING_INSTANCE_QUOTAS)==129
    assert {kind for _,kind in TRAINING_INSTANCE_QUOTAS}<=supported
    assert len(CHECKS)==len({code for code,_,_ in CHECKS})==140
    assert all(('cleanrooms-ml',code) in custom_keys() for code,_,_ in CHECKS)
