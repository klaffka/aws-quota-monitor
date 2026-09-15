import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import fsx, medialive
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

CLUSTER = 'cluster-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def medialive_input(identity, kind, location=None, vpc=False):
    entry = {'Id': identity, 'Name': identity, 'Type': kind}
    if location is not None:
        entry['InputNetworkLocation'] = location
    if vpc:
        entry['Destinations'] = [{'Vpc': {'AvailabilityZone': 'eu-central-1a',
                                          'NetworkInterfaceId': 'eni-1'}}]
    return entry


def test_inputs_are_grouped_by_type_location_and_vpc_destination():
    entries = [medialive_input('i1', 'RTP_PUSH'), medialive_input('i2', 'UDP_PUSH'),
               medialive_input('i3', 'URL_PULL'),
               medialive_input('i4', 'INPUT_DEVICE'),
               medialive_input('i5', 'MEDIACONNECT'),
               medialive_input('i6', 'MEDIACONNECT_ROUTER'),
               medialive_input('i7', 'SDI', location='ON_PREMISES'),
               medialive_input('i8', 'RTMP_PUSH', vpc=True)]
    for code, expected in (('L-9E233AF7', 3), ('L-BDF24E14', 1), ('L-FBCE2FC3', 2),
                           ('L-A4814CCC', 1), ('L-68E02936', 1)):
        ctx = context('medialive', code)
        with Stubber(ctx.client('medialive')) as stub:
            stub.add_response('list_inputs', {'Inputs': entries}, {})
            assert check(medialive, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_an_unknown_input_type_raises_nodata():
    ctx = context('medialive', 'L-9E233AF7')
    with Stubber(ctx.client('medialive')) as stub:
        stub.add_response('list_inputs', {'Inputs': [
            {'Id': 'i1', 'Name': 'i1', 'Type': 'CARRIER_PIGEON'}]}, {})
        with pytest.raises(NoData, match='unknown type'):
            check(medialive, 'L-9E233AF7')(ctx)


def test_channels_are_grouped_by_codec_resolution_and_cdi():
    entries = [{'Id': 'c1', 'Name': 'c1',
                'InputSpecification': {'Codec': 'HEVC', 'Resolution': 'UHD'}},
               {'Id': 'c2', 'Name': 'c2',
                'InputSpecification': {'Codec': 'AVC', 'Resolution': 'HD'},
                'CdiInputSpecification': {'Resolution': 'FHD'}},
               {'Id': 'c3', 'Name': 'c3'}]
    for code, expected in (('L-05A796F2', 1), ('L-DDE858F0', 1), ('L-3FDA265B', 1)):
        ctx = context('medialive', code)
        with Stubber(ctx.client('medialive')) as stub:
            stub.add_response('list_channels', {'Channels': entries}, {})
            assert check(medialive, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_cluster_children_are_reported_per_cluster():
    ctx = context('medialive', 'L-22ED1BEF')
    with Stubber(ctx.client('medialive')) as stub:
        stub.add_response('list_clusters', {'Clusters': [
            {'Id': CLUSTER, 'Name': 'edge'}, {'Id': 'cluster-2', 'Name': 'core'}]}, {})
        stub.add_response('list_nodes', {'Nodes': [{'Id': 'n1'}, {'Id': 'n2'}]},
                          {'ClusterId': CLUSTER})
        stub.add_response('list_nodes', {'Nodes': [{'Id': 'n3'}]},
                          {'ClusterId': 'cluster-2'})
        result = check(medialive, 'L-22ED1BEF')(ctx)
        assert (result['usage'], result['resource_id']) == (2, CLUSTER)
        stub.assert_no_pending_responses()


def file_system(identity, kind, capacity, storage='SSD', configuration=None):
    result = {'FileSystemId': identity, 'FileSystemType': kind,
              'StorageCapacity': capacity, 'StorageType': storage}
    if configuration:
        result.update(configuration)
    return result


def test_storage_capacity_is_summed_per_type_and_storage_class():
    systems = [file_system('fs-0123456789abcdef1', 'WINDOWS', 1024),
               file_system('fs-0123456789abcdef2', 'WINDOWS', 2048),
               file_system('fs-0123456789abcdef3', 'WINDOWS', 4096, storage='HDD'),
               file_system('fs-0123456789abcdef4', 'ONTAP', 8192)]
    for code, expected in (('L-E43BDB2E', 3072), ('L-84EAF187', 4096),
                           ('L-E2C89679', 8192)):
        ctx = context('fsx', code)
        with Stubber(ctx.client('fsx')) as stub:
            stub.add_response('describe_file_systems', {'FileSystems': systems}, {})
            assert check(fsx, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_the_per_file_system_quota_reports_the_largest_one():
    ctx = context('fsx', 'L-7D5FDD38')
    with Stubber(ctx.client('fsx')) as stub:
        stub.add_response('describe_file_systems', {'FileSystems': [
            file_system('fs-0123456789abcdef1', 'OPENZFS', 1024),
            file_system('fs-0123456789abcdef2', 'OPENZFS', 8192)]}, {})
        result = check(fsx, 'L-7D5FDD38')(ctx)
        assert (result['usage'], result['resource_id']) == (8192, 'fs-0123456789abcdef2')
        stub.assert_no_pending_responses()


def test_throughput_and_iops_come_from_the_type_configuration():
    systems = [file_system('fs-0123456789abcdef1', 'WINDOWS', 1024, configuration={
        'WindowsConfiguration': {'ThroughputCapacity': 512,
                                 'DiskIopsConfiguration': {'Mode': 'USER_PROVISIONED',
                                                           'Iops': 40000}}}),
               file_system('fs-0123456789abcdef2', 'WINDOWS', 1024, configuration={
                   'WindowsConfiguration': {'ThroughputCapacity': 256}})]
    for code, expected in (('L-FD89CA8A', 768), ('L-901C77F5', 40000)):
        ctx = context('fsx', code)
        with Stubber(ctx.client('fsx')) as stub:
            stub.add_response('describe_file_systems', {'FileSystems': systems}, {})
            assert check(fsx, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_backups_are_counted_per_file_system_type():
    backups = [{'BackupId': 'backup-0123456789abcdef1', 'Lifecycle': 'AVAILABLE', 'Type': 'USER_INITIATED',
                'CreationTime': '2026-09-15T00:00:00Z',
                'FileSystem': {'FileSystemId': 'fs-0123456789abcdef1', 'FileSystemType': 'WINDOWS'}},
               {'BackupId': 'backup-0123456789abcdef2', 'Lifecycle': 'AVAILABLE', 'Type': 'AUTOMATIC',
                'CreationTime': '2026-09-15T00:00:00Z',
                'FileSystem': {'FileSystemId': 'fs-0123456789abcdef2', 'FileSystemType': 'LUSTRE'}}]
    for code, expected in (('L-E94C1C19', 1), ('L-CD5E0524', 1), ('L-C431DBA3', 0)):
        ctx = context('fsx', code)
        with Stubber(ctx.client('fsx')) as stub:
            stub.add_response('describe_backups', {'Backups': backups}, {})
            assert check(fsx, code)(ctx)['usage'] == expected, code
            stub.assert_no_pending_responses()


def test_file_caches_are_counted_separately_from_file_systems():
    ctx = context('fsx', 'L-15D9FE87')
    with Stubber(ctx.client('fsx')) as stub:
        stub.add_response('describe_file_caches', {'FileCaches': [
            {'FileCacheId': 'fc-0123456789abcdef1', 'FileCacheType': 'LUSTRE', 'StorageCapacity': 2400},
            {'FileCacheId': 'fc-0123456789abcdef2', 'FileCacheType': 'LUSTRE', 'StorageCapacity': 1200}]}, {})
        assert fsx.cache_storage_capacity(ctx)['usage'] == 3600
        stub.assert_no_pending_responses()


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((medialive, 'medialive'), (fsx, 'fsx')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
