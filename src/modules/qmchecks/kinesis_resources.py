"""Amazon Kinesis stream shard inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


def shard_count(ctx):
    total = 0
    for stream in ctx.call('kinesis', 'list_streams', 'StreamNames'):
        total += len(ctx.call('kinesis', 'list_shards', 'Shards', StreamName=stream))
    return dict(usage=total, source='kinesis:ListShards', method='ACCOUNT_COUNT')


CHECKS = [('L-0918CF54', 'Shards per Region', shard_count)]


def get_current_quotastatus_kinesis_resources(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kinesis' for service, _ in context.quotas):
        return []
    return context.run('kinesis', CHECKS, skip)
