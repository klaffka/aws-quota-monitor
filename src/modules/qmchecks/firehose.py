"""Amazon Data Firehose regional delivery-stream inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


def delivery_streams(ctx):
    return ctx.call('firehose', 'list_delivery_streams', 'DeliveryStreamNames')


CHECKS = [
    ('L-14BB0BE7', 'Delivery streams',
     lambda ctx: dict(usage=len(delivery_streams(ctx)), source='firehose:ListDeliveryStreams',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_firehose(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'firehose' for service, _ in context.quotas):
        return []
    return context.run('firehose', CHECKS, skip)
