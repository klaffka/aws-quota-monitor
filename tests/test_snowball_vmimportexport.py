import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import snowball, vmimportexport
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 10}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def job(identity, kind, state='WithCustomer'):
    return {'JobId': identity, 'JobState': state, 'SnowballType': kind,
            'JobType': 'IMPORT'}


def test_devices_are_counted_by_family_and_exclude_returned_jobs():
    jobs = [job('JID1', 'EDGE_S'), job('JID2', 'V3_5C'),
            job('JID3', 'EDGE_C', 'Complete'), job('JID4', 'SNC1_SSD'),
            job('JID5', 'SNC1_HDD', 'Cancelled')]
    for code, expected in (('L-B6883B9F', 2), ('L-9F53AA61', 1)):
        ctx = context('snowball', code)
        with Stubber(ctx.client('snowball')) as stub:
            stub.add_response('list_jobs', {'JobListEntries': jobs}, {})
            assert check(snowball, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_an_unknown_device_type_raises_nodata():
    ctx = context('snowball', 'L-B6883B9F')
    with Stubber(ctx.client('snowball')) as stub:
        stub.add_response('list_jobs', {'JobListEntries': [
            {'JobId': 'JID1', 'JobState': 'WithCustomer'}]}, {})
        with pytest.raises(NoData, match='unknown device type'):
            check(snowball, 'L-B6883B9F')(ctx)


def test_image_and_snapshot_tasks_share_one_concurrency_count():
    ctx = context('vmimportexport', 'L-66ABAAD5')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_import_image_tasks', {'ImportImageTasks': [
            {'ImportTaskId': 'import-ami-1', 'Status': 'active'},
            {'ImportTaskId': 'import-ami-2', 'Status': 'completed'}]}, {})
        stub.add_response('describe_import_snapshot_tasks', {'ImportSnapshotTasks': [
            {'ImportTaskId': 'import-snap-1',
             'SnapshotTaskDetail': {'Status': 'active'}}]}, {})
        stub.add_response('describe_export_image_tasks', {'ExportImageTasks': [
            {'ExportImageTaskId': 'export-ami-1', 'Status': 'cancelling'},
            {'ExportImageTaskId': 'export-ami-2', 'Status': 'deleted'}]}, {})
        assert vmimportexport.image_and_snapshot_tasks(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_instance_and_volume_tasks_are_counted_separately():
    ctx = context('vmimportexport', 'L-0994E50B')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_conversion_tasks', {'ConversionTasks': [
            {'ConversionTaskId': 'import-i-1', 'State': 'active'},
            {'ConversionTaskId': 'import-i-2', 'State': 'cancelled'}]}, {})
        stub.add_response('describe_export_tasks', {'ExportTasks': [
            {'ExportTaskId': 'export-i-1', 'State': 'active'}]}, {})
        assert vmimportexport.instance_and_volume_tasks(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_an_import_snapshot_task_without_detail_raises_nodata():
    ctx = context('vmimportexport', 'L-66ABAAD5')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_import_image_tasks', {'ImportImageTasks': []}, {})
        stub.add_response('describe_import_snapshot_tasks', {'ImportSnapshotTasks': [
            {'ImportTaskId': 'import-snap-1'}]}, {})
        with pytest.raises(NoData, match='no detail'):
            vmimportexport.image_and_snapshot_tasks(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((snowball, 'snowball'),
                            (vmimportexport, 'vmimportexport')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
