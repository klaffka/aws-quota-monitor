"""Amazon S3 on Outposts bucket and access point quotas."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

OUTPOSTS = 'outposts'
S3CONTROL = 's3control'


def outposts(ctx):
    found = []
    for outpost in ctx.call(OUTPOSTS, 'list_outposts', 'Outposts'):
        identity = outpost.get('OutpostId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Outpost is missing its identity')
        if identity not in found:
            found.append(identity)
    return found


def buckets(outpost, ctx):
    found = {}
    for bucket in ctx.call(S3CONTROL, 'list_regional_buckets', 'RegionalBucketList',
                           AccountId=ctx.account, OutpostId=outpost):
        name = bucket.get('Bucket')
        arn = bucket.get('BucketArn')
        if not isinstance(name, str) or not name:
            raise NoData('Outpost bucket is missing its name')
        found[name] = arn or name
    return found


def buckets_per_outpost(ctx):
    values = [(outpost, len(buckets(outpost, ctx)), None) for outpost in outposts(ctx)]
    return maximum(values, 'Outpost', 's3control:ListRegionalBuckets')


def access_points_per_outpost(ctx):
    values = []
    for outpost in outposts(ctx):
        usage = 0
        for arn in buckets(outpost, ctx).values():
            points = ctx.call(S3CONTROL, 'list_access_points', 'AccessPointList',
                              AccountId=ctx.account, Bucket=arn)
            for point in points:
                if not isinstance(point.get('Name'), str):
                    raise NoData('Outpost access point is missing its name')
            usage += len(points)
        values.append((outpost, usage, None))
    return maximum(values, 'Outpost', 's3control:ListAccessPoints')


CHECKS = [
    ('L-CBA62F6C', 'Buckets', buckets_per_outpost),
    ('L-C39AA790', 'Access Points', access_points_per_outpost),
]


def get_current_quotastatus_s3_outposts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 's3-outposts' for service, _ in context.quotas):
        return []
    return context.run('s3-outposts', CHECKS, skip)
