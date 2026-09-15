from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import omics
from modules.qmcore.aws import CheckContext, NoData

STORE = '1234567890'
RUN = '1234567'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'omics', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in omics.CHECKS if candidate == code)


def test_omics_resource_checks_use_paginated_output_keys():
    # The plain inventories; every other check reads a status or a parent store.
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    counted = ['L-7CAE62CF', 'L-BFFBB2FD', 'L-899DA104', 'L-01A419C5', 'L-D91CDC5E']
    by_code = {code: fn for code, _, fn in omics.CHECKS}
    assert all(by_code[code](ctx)['usage'] == 2 for code in counted)


def run(identity, status, storage='STATIC'):
    return {'id': identity, 'status': status, 'storageType': storage}


def test_runs_are_split_by_state_and_storage_type():
    ctx = context('L-C9679DBC')
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_runs', {'items': [
            run('1111111', 'RUNNING'), run('2222222', 'COMPLETED'),
            run('3333333', 'PENDING', 'DYNAMIC'), run('4444444', 'DELETED')]}, {})
        assert check('L-C9679DBC')(ctx)['usage'] == 3
        assert check('L-A30FD31B')(ctx)['usage'] == 1
        assert check('L-BE38079A')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_an_unknown_run_status_raises_nodata():
    ctx = context('L-C9679DBC')
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_runs', {'items': [run(RUN, 'PAUSED')]}, {})
        with pytest.raises(NoData, match='unknown status'):
            check('L-C9679DBC')(ctx)


def test_tasks_and_gpus_are_counted_only_while_a_run_is_active():
    ctx = context('L-25504C8C')
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_runs', {'items': [
            run(RUN, 'RUNNING'), run('7654321', 'COMPLETED')]}, {})
        stub.add_response('list_run_tasks', {'items': [
            {'taskId': 't1', 'status': 'RUNNING', 'gpus': 2},
            {'taskId': 't2', 'status': 'PENDING'},
            {'taskId': 't3', 'status': 'COMPLETED', 'gpus': 8}]}, {'id': RUN})
        tasks = check('L-25504C8C')(ctx)
        assert (tasks['usage'], tasks['resource_id']) == (2, RUN)
        assert check('L-AFB19B96')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_read_sets_are_reported_for_the_fullest_sequence_store():
    ctx = context('L-BE766427')
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_sequence_stores', {'sequenceStores': [
            {'id': STORE, 'arn': 'arn:aws:omics:::sequenceStore/1', 'creationTime':
             '2026-09-15T00:00:00Z'},
            {'id': '9999999999', 'arn': 'arn:aws:omics:::sequenceStore/2',
             'creationTime': '2026-09-15T00:00:00Z'}]}, {})
        stub.add_response('list_read_sets', {'readSets': [
            {'id': '1111111111', 'arn': 'a', 'sequenceStoreId': STORE, 'status': 'ACTIVE',
             'fileType': 'FASTQ', 'creationTime': '2026-09-15T00:00:00Z'}]},
            {'sequenceStoreId': STORE})
        stub.add_response('list_read_sets', {'readSets': []},
                          {'sequenceStoreId': '9999999999'})
        result = check('L-BE766427')(ctx)
        assert (result['usage'], result['resource_id']) == (1, STORE)
        stub.assert_no_pending_responses()


def test_shares_are_grouped_by_the_resource_they_expose():
    ctx = context('L-4E5B34A1')
    workflow = 'arn:aws:omics:eu-central-1:123456789012:workflow/1234567'
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_shares', {'shares': [
            {'shareId': 's1', 'resourceArn': workflow, 'status': 'ACTIVE'},
            {'shareId': 's2', 'resourceArn': workflow, 'status': 'PENDING'},
            {'shareId': 's3', 'resourceArn': workflow + '2', 'status': 'ACTIVE'}]},
            {'resourceOwner': 'SELF', 'filter': {'type': ['WORKFLOW']}})
        result = check('L-4E5B34A1')(ctx)
        assert (result['usage'], result['resource_id']) == (2, workflow)
        stub.assert_no_pending_responses()


def test_store_imports_share_one_concurrency_quota():
    ctx = context('L-876AD0A2')
    with Stubber(ctx.client('omics')) as stub:
        stub.add_response('list_variant_import_jobs', {'variantImportJobs': [
            {'id': 'v1', 'destinationName': 'store', 'roleArn': 'arn:aws:iam::1:role/r',
             'status': 'IN_PROGRESS', 'creationTime': '2026-09-15T00:00:00Z',
             'updateTime': '2026-09-15T00:00:00Z'},
            {'id': 'v2', 'destinationName': 'store', 'roleArn': 'arn:aws:iam::1:role/r',
             'status': 'COMPLETED', 'creationTime': '2026-09-15T00:00:00Z',
             'updateTime': '2026-09-15T00:00:00Z'}]}, {})
        stub.add_response('list_annotation_import_jobs', {'annotationImportJobs': [
            {'id': 'a1', 'destinationName': 'store', 'versionName': 'version-one',
             'roleArn': 'arn:aws:iam::1:role/r', 'status': 'SUBMITTED',
             'creationTime': '2026-09-15T00:00:00Z',
             'updateTime': '2026-09-15T00:00:00Z'}]}, {})
        assert check('L-876AD0A2')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()
