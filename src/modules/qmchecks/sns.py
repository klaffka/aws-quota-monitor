"""Amazon SNS regional topic and subscription-policy inventories."""
from collections import Counter
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def _filter_policy_counts(ctx):
    """Return filter-policy counts keyed by topic ARN.

    Pending subscriptions have no usable attributes yet and are excluded.  A
    subscription can have at most one filter policy, so counting the non-empty
    ``FilterPolicy`` attribute directly matches the service quota semantics.
    """
    counts = Counter()
    for subscription in ctx.call('sns', 'list_subscriptions', 'Subscriptions'):
        arn = subscription.get('SubscriptionArn')
        topic = subscription.get('TopicArn')
        if not arn or arn == 'PendingConfirmation' or not topic:
            continue
        attributes = ctx.call('sns', 'get_subscription_attributes',
                              SubscriptionArn=arn).get('Attributes', {})
        if attributes.get('FilterPolicy'):
            counts[topic] += 1
    return counts


def filter_policies_per_topic(ctx):
    counts = _filter_policy_counts(ctx)
    return dict(usage=max(counts.values(), default=0), resource_type='SNSTopic',
                resource_id=max(counts, key=counts.get, default=None),
                source='sns:GetSubscriptionAttributes', method='PER_RESOURCE_MAX')


def filter_policies_per_account(ctx):
    return dict(usage=sum(_filter_policy_counts(ctx).values()),
                source='sns:GetSubscriptionAttributes', method='ACCOUNT_COUNT')


def subscriptions_per_topic(ctx):
    values = []
    for topic in ctx.call('sns', 'list_topics', 'Topics'):
        arn = topic.get('TopicArn')
        if arn:
            values.append((arn, len(ctx.call('sns', 'list_subscriptions_by_topic',
                                             'Subscriptions', TopicArn=arn)), None))
    return maximum(values, 'SNSTopic', 'sns:ListSubscriptionsByTopic')


CHECKS = [
    ('L-61103206', 'Topics per account',
     lambda ctx: dict(usage=len(ctx.call('sns', 'list_topics', 'Topics')),
                      source='sns:ListTopics', method='ACCOUNT_COUNT')),
    ('L-1A43D3DB', 'Pending subscriptions per account',
     lambda c: dict(usage=sum(s.get('SubscriptionArn') == 'PendingConfirmation'
                              for s in c.call('sns', 'list_subscriptions', 'Subscriptions')),
                    source='sns:ListSubscriptions', method='ACCOUNT_COUNT')),
    ('L-B96EDA7D', 'Filter policies per topic', filter_policies_per_topic),
    ('L-4126E74A', 'Filter policies per account', filter_policies_per_account),
    ('L-A4340BCD', 'Subscriptions per topic', subscriptions_per_topic),
]


def get_current_quotastatus_sns(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'sns' for service, _ in context.quotas):
        return []
    return context.run('sns', CHECKS, skip)
