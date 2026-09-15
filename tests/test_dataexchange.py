from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import dataexchange
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)
ACCOUNT = '123456789012'
DATA_SET = '11111111111111111111111111111111'
OTHER_SET = '22222222222222222222222222222222'
REVISION = '33333333333333333333333333333333'


def context(code='L-52E2E63A'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'dataexchange', 'QuotaCode': code,
                          'Value': 100}], account=ACCOUNT)


def check(code):
    return next(fn for quota, _, fn in dataexchange.CHECKS if quota == code)


def data_set(identity, asset_type='S3_SNAPSHOT'):
    return {'Id': identity, 'Arn': f'arn:aws:dataexchange:::data-sets/{identity}',
            'AssetType': asset_type, 'CreatedAt': NOW, 'Description': identity,
            'Name': identity, 'Origin': 'OWNED', 'UpdatedAt': NOW}


def revision(identity, data_set_id=DATA_SET):
    return {'Id': identity, 'Arn': f'arn:aws:dataexchange:::revisions/{identity}',
            'DataSetId': data_set_id, 'CreatedAt': NOW, 'UpdatedAt': NOW}


def test_revisions_are_counted_per_data_set_and_per_asset_type():
    sets = [data_set(DATA_SET, 'S3_SNAPSHOT'), data_set(OTHER_SET, 'API_GATEWAY_API')]
    ctx = context('L-375806A0')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_sets', {'DataSets': sets}, {})
        stub.add_response('list_data_set_revisions', {'Revisions': [
            revision(REVISION)]}, {'DataSetId': DATA_SET})
        stub.add_response('list_data_set_revisions', {'Revisions': [
            revision('44444444444444444444444444444444', OTHER_SET),
            revision('55555555555555555555555555555555', OTHER_SET)]},
            {'DataSetId': OTHER_SET})
        result = check('L-375806A0')(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_SET)
        stub.assert_no_pending_responses()
    ctx = context('L-70B0F91E')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_sets', {'DataSets': [
            data_set(DATA_SET, 'S3_DATA_ACCESS'), data_set(OTHER_SET, 'S3_SNAPSHOT')]}, {})
        stub.add_response('list_data_set_revisions', {'Revisions': [revision(REVISION)]},
                          {'DataSetId': DATA_SET})
        # Only the S3 data access data set counts towards its own quota.
        result = check('L-70B0F91E')(ctx)
        assert (result['usage'], result['resource_id']) == (1, DATA_SET)
        stub.assert_no_pending_responses()


def test_an_unknown_asset_type_raises_nodata():
    ctx = context('L-52E2E63A')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_sets', {'DataSets': [
            dict(data_set(DATA_SET), AssetType='CRYSTAL_BALL')]}, {})
        with pytest.raises(NoData, match='unknown asset type'):
            check('L-52E2E63A')(ctx)


def job(identity, state, kind):
    return {'Id': identity, 'Arn': f'arn:aws:dataexchange:::jobs/{identity}',
            'State': state, 'Type': kind, 'CreatedAt': NOW, 'UpdatedAt': NOW,
            'Details': {}}


def test_running_jobs_are_grouped_by_type():
    jobs = [job('j1', 'IN_PROGRESS', 'IMPORT_ASSETS_FROM_S3'),
            job('j2', 'WAITING', 'IMPORT_ASSETS_FROM_S3'),
            job('j3', 'COMPLETED', 'IMPORT_ASSETS_FROM_S3'),
            job('j4', 'IN_PROGRESS', 'EXPORT_ASSETS_TO_S3')]
    for code, expected in (('L-307F71B5', 2), ('L-37C425C6', 1), ('L-50515269', 0)):
        ctx = context(code)
        with Stubber(ctx.client('dataexchange')) as stub:
            stub.add_response('list_jobs', {'Jobs': jobs}, {})
            assert check(code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def grant(identity, state, receiver='111111111111'):
    return {'Id': identity, 'Arn': f'arn:aws:dataexchange:::data-grants/{identity}',
            'Name': identity, 'SenderPrincipal': ACCOUNT,
            'ReceiverPrincipal': receiver, 'AcceptanceState': state,
            'DataSetId': DATA_SET, 'SourceDataSetId': DATA_SET,
            'CreatedAt': NOW, 'UpdatedAt': NOW}


def test_data_grants_are_counted_in_total_and_pending_per_consumer():
    grants = [grant('g1', 'ACCEPTED'),
              grant('g2', 'PENDING_RECEIVER_ACCEPTANCE'),
              grant('g3', 'PENDING_RECEIVER_ACCEPTANCE'),
              grant('g4', 'PENDING_RECEIVER_ACCEPTANCE', '222222222222')]
    ctx = context('L-4F23AFE3')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_grants', {'DataGrantSummaries': grants}, {})
        assert dataexchange.active_and_pending_data_grants(ctx)['usage'] == 4
        stub.assert_no_pending_responses()
    ctx = context('L-1FA7039C')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_grants', {'DataGrantSummaries': grants}, {})
        result = dataexchange.pending_grants_per_consumer(ctx)
        assert (result['usage'], result['resource_id']) == (2, '111111111111')
        stub.assert_no_pending_responses()


def test_event_actions_are_counted_per_source_data_set():
    ctx = context('L-7053BE85')
    with Stubber(ctx.client('dataexchange')) as stub:
        stub.add_response('list_data_sets', {'DataSets': [
            data_set(DATA_SET), data_set(OTHER_SET)]}, {})
        stub.add_response('list_event_actions', {'EventActions': [
            {'Id': 'e1', 'Arn': 'arn:aws:dataexchange:::event-actions/e1',
             'CreatedAt': NOW, 'UpdatedAt': NOW,
             'Action': {'ExportRevisionToS3': {'RevisionDestination': {
                 'Bucket': 'exports'}}},
             'Event': {'RevisionPublished': {'DataSetId': DATA_SET}}}]}, {})
        result = dataexchange.event_actions_per_data_set(ctx)
        assert (result['usage'], result['resource_id']) == (1, DATA_SET)
        stub.assert_no_pending_responses()


def test_every_dataexchange_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'dataexchange'}
    assert {code for code, _, _ in dataexchange.CHECKS} <= registered
