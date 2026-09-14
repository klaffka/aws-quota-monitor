"""AWS Storage Gateway regional per-gateway resource quotas."""
from collections import Counter
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def gateways(ctx):
    return ctx.call('storagegateway', 'list_gateways', 'Gateways')


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
]


def get_current_quotastatus_storagegateway(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'storagegateway' for service, _ in context.quotas):
        return []
    return context.run('storagegateway', CHECKS, skip)
