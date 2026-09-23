"""S3 account-level access point and Multi-Region Access Point inventories."""
from botocore.exceptions import ClientError
from modules.qmcore.aws import CheckContext, maximum, session_from_env

# Multi-Region Access Points are account-global and their control plane
# answers only in us-west-2, whatever Region the collector runs in.
MRAP_REGION = 'us-west-2'

def replication_rules_per_bucket(c):
    values = []
    for bucket in c.call('s3', 'list_buckets', 'Buckets'):
        name = bucket.get('Name')
        if not name:
            continue
        try:
            rules = c.call('s3', 'get_bucket_replication', Bucket=name).get('ReplicationConfiguration', {}).get('Rules', [])
        except ClientError as exc:
            # A bucket without replication answers with this error: zero rules.
            if exc.response['Error']['Code'] != 'ReplicationConfigurationNotFoundError':
                raise
            rules = []
        values.append((name, len(rules), None))
    return maximum(values, 'S3Bucket', 's3:GetBucketReplication')


def lifecycle_rules_per_bucket(c):
    values = []
    for bucket in c.call('s3', 'list_buckets', 'Buckets'):
        name = bucket.get('Name')
        if not name:
            continue
        try:
            rules = c.call('s3', 'get_bucket_lifecycle_configuration',
                           Bucket=name).get('Rules', [])
        except Exception as exc:
            if 'NoSuchLifecycleConfiguration' in str(exc):
                rules = []
            else:
                raise
        values.append((name, len(rules), None))
    return maximum(values, 'S3Bucket', 's3:GetBucketLifecycleConfiguration')


def bucket_event_notifications_per_bucket(c):
    values = []
    for bucket in c.call('s3', 'list_buckets', 'Buckets'):
        name = bucket.get('Name')
        if not name:
            continue
        config = c.call('s3', 'get_bucket_notification_configuration', Bucket=name)
        total = sum(len(config.get(key, [])) for key in
                    ('TopicConfigurations', 'QueueConfigurations', 'LambdaFunctionConfigurations'))
        values.append((name, total, None))
    return maximum(values, 'S3Bucket', 's3:GetBucketNotificationConfiguration')


def bucket_tags_per_bucket(c):
    values = []
    for bucket in c.call('s3', 'list_buckets', 'Buckets'):
        name = bucket.get('Name')
        if name:
            config = c.call('s3', 'get_bucket_tagging', Bucket=name)
            values.append((name, len(config.get('TagSet', [])), None))
    return maximum(values, 'S3Bucket', 's3:GetBucketTagging')


CHECKS = [
    ('L-B461D596', 'Replication rules', replication_rules_per_bucket),
    ('L-146D5F0C', 'Lifecycle rules', lifecycle_rules_per_bucket),
    ('L-3E24E5F9', 'Event notifications', bucket_event_notifications_per_bucket),
    ('L-55BA2C6C', 'Bucket tags', bucket_tags_per_bucket),
    ('L-FAABEEBA', 'Access Points',
     lambda c: dict(usage=len(c.call('s3control', 'list_access_points', 'AccessPointList',
                                     AccountId=c.account)),
                    source='s3control:ListAccessPoints', method='ACCOUNT_COUNT')),
    ('L-881EA1F4', 'Multi-Region Access Points',
     lambda c: dict(usage=len(c.in_region(MRAP_REGION).call(
                        's3control', 'list_multi_region_access_points', 'AccessPoints',
                        AccountId=c.account)),
                    source='s3control:ListMultiRegionAccessPoints', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_s3(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 's3' for service, _ in context.quotas):
        return []
    return context.run('s3', CHECKS, skip)
