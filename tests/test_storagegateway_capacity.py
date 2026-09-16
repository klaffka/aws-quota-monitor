import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import storagegateway as sgw
from modules.qmcore.aws import CheckContext, NoData

GATEWAY = 'arn:aws:storagegateway:eu-central-1:123456789012:gateway/sgw-11111111'
OTHER = 'arn:aws:storagegateway:eu-central-1:123456789012:gateway/sgw-22222222'
TIB = 1024 ** 4
TAPE = GATEWAY + '/tape/AMZN{:0>8}'
VOLUME = GATEWAY + '/volume/vol-{:0>17}'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'storagegateway', 'QuotaCode': code,
                          'Value': 32}], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in sgw.CHECKS if candidate == code)


def tape(arn, gateway, size):
    return {'TapeARN': arn, 'GatewayARN': gateway, 'TapeSizeInBytes': size,
            'TapeBarcode': 'TEST01', 'TapeStatus': 'AVAILABLE'}


def volume(arn, gateway, kind, size):
    return {'VolumeARN': arn, 'GatewayARN': gateway, 'VolumeType': kind,
            'VolumeSizeInBytes': size}


def test_tapes_are_counted_and_summed_per_library():
    ctx = context('L-2232E8E3')
    with Stubber(ctx.client('storagegateway')) as stub:
        stub.add_response('list_tapes', {'TapeInfos': [
            tape(TAPE.format(1), GATEWAY, TIB), tape(TAPE.format(2), GATEWAY, 2 * TIB),
            tape(TAPE.format(3), OTHER, 3 * TIB)]}, {})
        count = check('L-2232E8E3')(ctx)
        assert (count['usage'], count['resource_id']) == (2, GATEWAY)
        # One shared inventory answers the size checks too.
        assert check('L-4951D254')(ctx)['usage'] == pytest.approx(3 / 1024)
        largest = check('L-311F8856')(ctx)
        assert (largest['usage'], largest['resource_id']) == (3, TAPE.format(3))
        stub.assert_no_pending_responses()


def test_volume_sizes_are_reported_per_volume_and_per_gateway():
    ctx = context('L-2E88EE16')
    with Stubber(ctx.client('storagegateway')) as stub:
        stub.add_response('list_volumes', {'VolumeInfos': [
            volume(VOLUME.format(1), GATEWAY, 'CACHED', TIB),
            volume(VOLUME.format(2), GATEWAY, 'CACHED', 4 * TIB),
            volume(VOLUME.format(3), OTHER, 'STORED', 2 * TIB)]}, {})
        largest = check('L-2E88EE16')(ctx)
        assert (largest['usage'], largest['resource_id']) == (4, VOLUME.format(2))
        per_gateway = check('L-6F75AC83')(ctx)
        assert (per_gateway['usage'], per_gateway['resource_id']) == (5, GATEWAY)
        # A stored volume never counts against the cached volume quotas.
        assert check('L-81A6E497')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_allocated_capacity_is_read_only_for_gateways_that_have_it():
    ctx = context('L-59D49F15')
    with Stubber(ctx.client('storagegateway')) as stub:
        stub.add_response('list_gateways', {'Gateways': [
            {'GatewayARN': GATEWAY, 'GatewayType': 'VTL'},
            {'GatewayARN': OTHER, 'GatewayType': 'STORED'}]}, {})
        stub.add_response('describe_cache', {'GatewayARN': GATEWAY,
                                             'CacheAllocatedInBytes': 2 * TIB},
                          {'GatewayARN': GATEWAY})
        result = check('L-59D49F15')(ctx)
        assert (result['usage'], result['resource_id']) == (2, GATEWAY)
        # The stored volume gateway has no cache, so no call is made for it.
        stub.assert_no_pending_responses()


def test_an_unknown_gateway_type_raises_nodata():
    ctx = context('L-59D49F15')
    with Stubber(ctx.client('storagegateway')) as stub:
        stub.add_response('list_gateways', {'Gateways': [
            {'GatewayARN': GATEWAY, 'GatewayType': 'TAPE_ROBOT'}]}, {})
        with pytest.raises(NoData, match='unknown gateway type'):
            check('L-59D49F15')(ctx)
