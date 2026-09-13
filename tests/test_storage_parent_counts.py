from unittest.mock import Mock

from modules.qmchecks.efs import access_points_per_file_system
from modules.qmchecks.storagegateway import shares_per_bucket


def test_efs_access_points_use_maximum_per_file_system():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'FileSystemId': 'fs-1'}, {'FileSystemId': 'fs-2'}],
        [{'AccessPointId': 'ap-1'}, {'AccessPointId': 'ap-2'}],
        [{'AccessPointId': 'ap-3'}],
    ]
    result = access_points_per_file_system(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'fs-1')


def test_storage_gateway_file_shares_use_maximum_per_s3_bucket():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'GatewayARN': 'gw-1'}, {'GatewayARN': 'gw-2'}],
        [{'S3BucketName': 'bucket-a'}, {'S3BucketName': 'bucket-a'}],
        [{'S3BucketName': 'bucket-a'}, {'S3BucketName': 'bucket-b'}],
    ]
    result = shares_per_bucket(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'bucket-a')
