"""AWS Storage Gateway regional per-gateway resource and capacity quotas.

Capacities are reported in the unit each quota names: tape libraries in PiB,
everything else in TiB, converted from the bytes the API returns.
"""
from collections import Counter, defaultdict
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

STORAGEGATEWAY = 'storagegateway'
GATEWAY_TYPES = {'STORED', 'CACHED', 'VTL', 'VTL_SNOWBALL', 'FILE_S3',
                 'FILE_FSX_SMB'}
TAPE_TYPES = {'VTL', 'VTL_SNOWBALL'}
FILE_TYPES = {'FILE_S3', 'FILE_FSX_SMB'}
# A stored volume gateway keeps the full volume on disk and has no cache; a
# file gateway uploads through its cache and has no upload buffer.
CACHE_TYPES = GATEWAY_TYPES - {'STORED'}
BUFFER_TYPES = GATEWAY_TYPES - FILE_TYPES
TIB = 1024 ** 4
PIB = 1024 ** 5
VOLUME_TYPES = {'STORED', 'CACHED'}


def gateways(ctx):
    return ctx.call(STORAGEGATEWAY, 'list_gateways', 'Gateways')


def _typed(ctx, types):
    """Yield the gateways of one kind, rejecting a type the catalog cannot map."""
    for gateway in gateways(ctx):
        kind = gateway.get('GatewayType')
        if kind not in GATEWAY_TYPES:
            raise NoData('Storage Gateway has an unknown gateway type')
        if kind in types:
            yield gateway


def _bytes(entry, field, subject):
    value = entry.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise NoData(f'Storage Gateway {subject} has no valid {field}')
    return value


def tapes(ctx):
    """Group every virtual tape by the gateway that holds it."""
    found = defaultdict(list)
    for tape in ctx.call(STORAGEGATEWAY, 'list_tapes', 'TapeInfos'):
        arn = tape.get('GatewayARN')
        if not isinstance(arn, str) or not arn:
            raise NoData('Storage Gateway tape is missing its gateway')
        found[arn].append(tape)
    return found


def tapes_per_library(ctx):
    return maximum(((arn, len(entries), None) for arn, entries in tapes(ctx).items()),
                   'StorageGateway', 'storagegateway:ListTapes')


def tape_library_size(ctx):
    values = [(arn, sum(_bytes(tape, 'TapeSizeInBytes', 'tape')
                        for tape in entries) / PIB, None)
              for arn, entries in tapes(ctx).items()]
    return maximum(values, 'StorageGateway', 'storagegateway:ListTapes')


def largest_tape(ctx):
    values = [(tape.get('TapeARN'), _bytes(tape, 'TapeSizeInBytes', 'tape') / TIB, None)
              for entries in tapes(ctx).values() for tape in entries]
    return maximum(values, 'StorageGatewayTape', 'storagegateway:ListTapes')


def volumes(ctx, volume_type):
    found = defaultdict(list)
    for volume in ctx.call(STORAGEGATEWAY, 'list_volumes', 'VolumeInfos'):
        kind = volume.get('VolumeType')
        if kind is not None and kind not in VOLUME_TYPES:
            raise NoData('Storage Gateway volume has an unknown type')
        if kind == volume_type:
            found[volume.get('GatewayARN')].append(volume)
    return found


def _largest_volume(volume_type):
    def check(ctx):
        values = [(volume.get('VolumeARN'),
                   _bytes(volume, 'VolumeSizeInBytes', 'volume') / TIB, None)
                  for entries in volumes(ctx, volume_type).values()
                  for volume in entries]
        return maximum(values, 'StorageGatewayVolume', 'storagegateway:ListVolumes')
    return check


def _volume_size_per_gateway(volume_type):
    def check(ctx):
        values = [(arn, sum(_bytes(volume, 'VolumeSizeInBytes', 'volume')
                            for volume in entries) / TIB, None)
                  for arn, entries in volumes(ctx, volume_type).items()]
        return maximum(values, 'StorageGateway', 'storagegateway:ListVolumes')
    return check


def _allocated(method, field, types):
    """Report the disk a gateway has allocated, per gateway, in TiB."""
    def check(ctx):
        values = []
        for gateway in _typed(ctx, types):
            arn = gateway.get('GatewayARN')
            response = ctx.call(STORAGEGATEWAY, method, GatewayARN=arn)
            values.append((arn, _bytes(response, field, 'gateway') / TIB, None))
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return maximum(values, 'StorageGateway', f'storagegateway:{operation}')
    return check


def per_gateway(ctx, method, key, quota_type=None):
    values = []
    for gateway in gateways(ctx):
        arn = gateway.get('GatewayARN')
        resources = ctx.call('storagegateway', method, key, GatewayARN=arn)
        if quota_type:
            resources = [item for item in resources if item.get('VolumeType') == quota_type]
        values.append((arn, len(resources), None))
    return maximum(values, 'StorageGateway', f'storagegateway:{method}')


def shares_per_bucket(ctx):
    counts = Counter()
    for gateway in gateways(ctx):
        for share in ctx.call('storagegateway', 'list_file_shares', 'FileShareInfoList',
                              GatewayARN=gateway.get('GatewayARN')):
            bucket = share.get('S3BucketName')
            if bucket:
                counts[bucket] += 1
    return maximum([(bucket, count, None) for bucket, count in counts.items()],
                   'S3Bucket', 'storagegateway:ListFileShares')


CHECKS = [
    ('L-7B01AFFB', 'Stored volumes per gateway',
     lambda ctx: per_gateway(ctx, 'list_volumes', 'VolumeInfos', 'STORED')),
    ('L-761F1680', 'Cached volumes per gateway',
     lambda ctx: per_gateway(ctx, 'list_volumes', 'VolumeInfos', 'CACHED')),
    ('L-58DCC961', 'File shares per gateway',
     lambda ctx: per_gateway(ctx, 'list_file_shares', 'FileShareInfoList')),
    ('L-CEFD39A0', 'File shares per S3 bucket', shares_per_bucket),
    ('L-2232E8E3', 'Max virtual tapes in a VTL', tapes_per_library),
    ('L-4951D254', 'Total size of tapes in a virtual tape library in PiB',
     tape_library_size),
    ('L-311F8856', 'Max size of a virtual tape in TiB', largest_tape),
    ('L-2E88EE16', 'Cached volume size in TiB', _largest_volume('CACHED')),
    ('L-81A6E497', 'Stored volume size in TiB', _largest_volume('STORED')),
    ('L-6F75AC83', 'Size of all cached volumes per gateway in TiB',
     _volume_size_per_gateway('CACHED')),
    ('L-5308FBCA', 'Size of all stored volumes per gateway in TiB',
     _volume_size_per_gateway('STORED')),
    ('L-14F83003', 'Cached volume gateway Cache Maximum in TiB',
     _allocated('describe_cache', 'CacheAllocatedInBytes', {'CACHED'})),
    ('L-59D49F15', 'Tape gateway Cache Maximum in TiB',
     _allocated('describe_cache', 'CacheAllocatedInBytes', TAPE_TYPES)),
    ('L-F5915598', 'File gateway Cache Maximum in TiB',
     _allocated('describe_cache', 'CacheAllocatedInBytes', FILE_TYPES)),
    ('L-FF1BE522', 'Cached volume gateway Upload Buffer Maximum in TiB',
     _allocated('describe_upload_buffer', 'UploadBufferAllocatedInBytes', {'CACHED'})),
    ('L-2EC26EAB', 'Tape gateway Upload Buffer Maximum in TiB',
     _allocated('describe_upload_buffer', 'UploadBufferAllocatedInBytes', TAPE_TYPES)),
    ('L-99E991AF', 'Stored volume gateway Upload Buffer Maximum in TiB',
     _allocated('describe_upload_buffer', 'UploadBufferAllocatedInBytes', {'STORED'})),
]


def get_current_quotastatus_storagegateway(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'storagegateway' for service, _ in context.quotas):
        return []
    return context.run('storagegateway', CHECKS, skip)
