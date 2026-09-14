"""Amazon SQS queue configuration, policy and tag quotas.

Message batch and per-message limits (`Attributes per Message`, `Messages per
Batch`, `Batched Message ID Length`, `Message Size in S3 Bucket`) apply to a
single request and leave no inventory behind, so they are not measured here.
"""
import json
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SQS = 'sqs'


def _queue_name(url):
    name = str(url or '').rsplit('/', 1)[-1]
    if not name:
        raise NoData('SQS queue URL has no name')
    return name


def queues(ctx):
    found = {}
    for url in ctx.call(SQS, 'list_queues', 'QueueUrls'):
        if not isinstance(url, str) or not url:
            raise NoData('SQS queue inventory contains an invalid URL')
        if url in found:
            continue
        found[url] = _queue_name(url)
    return found


def attributes(url, ctx):
    result = ctx.call(SQS, 'get_queue_attributes', QueueUrl=url,
                      AttributeNames=['All']).get('Attributes')
    if not isinstance(result, dict) or not result:
        raise NoData('SQS queue has no attributes')
    return result


def _number(value, subject):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise NoData(f'SQS {subject} is not a number') from None


def _attribute_maximum(name, subject, source='sqs:GetQueueAttributes'):
    """Report the largest configured value of one queue attribute."""
    def check(ctx):
        values = [(url, _number(attributes(url, ctx).get(name), subject), None)
                  for url in queues(ctx)]
        return maximum(values, 'SQSQueue', source)
    return check


def _policy(url, ctx):
    """Return the queue policy document, or None when the queue has none."""
    document = attributes(url, ctx).get('Policy')
    if document is None:
        return None
    if not isinstance(document, str) or not document:
        raise NoData('SQS queue policy is empty')
    try:
        policy = json.loads(document)
    except ValueError:
        raise NoData('SQS queue policy is not valid JSON') from None
    if not isinstance(policy, dict):
        raise NoData('SQS queue policy is not a document')
    return policy


def _statements(policy):
    statements = policy.get('Statement')
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list) or not statements:
        raise NoData('SQS queue policy has no statements')
    for statement in statements:
        if not isinstance(statement, dict):
            raise NoData('SQS queue policy has an invalid statement')
    return statements


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _conditions(statement):
    condition = statement.get('Condition')
    if condition is None:
        return 0
    if not isinstance(condition, dict):
        raise NoData('SQS queue policy has an invalid condition')
    total = 0
    for keys in condition.values():
        if not isinstance(keys, dict):
            raise NoData('SQS queue policy has an invalid condition operator')
        total += len(keys)
    return total


def _principals(statement):
    total = 0
    for key in ('Principal', 'NotPrincipal'):
        principal = statement.get(key)
        if principal is None:
            continue
        if isinstance(principal, str):
            total += 1
        elif isinstance(principal, dict):
            total += sum(len(_as_list(value)) for value in principal.values())
        else:
            raise NoData('SQS queue policy has an invalid principal')
    return total


def _policy_maximum(measure, source='sqs:GetQueueAttributes'):
    def check(ctx):
        values = []
        for url in queues(ctx):
            policy = _policy(url, ctx)
            values.append((url, 0 if policy is None else measure(policy), None))
        return maximum(values, 'SQSQueue', source)
    return check


def _policy_size(ctx):
    values = []
    for url in queues(ctx):
        document = attributes(url, ctx).get('Policy') or ''
        values.append((url, len(document.encode('utf-8')), None))
    return maximum(values, 'SQSQueue', 'sqs:GetQueueAttributes')


def in_flight_messages(ctx):
    """FIFO queues have their own in-flight quota, so only standard queues count."""
    values = []
    for url in queues(ctx):
        attrs = attributes(url, ctx)
        if attrs.get('FifoQueue') == 'true':
            continue
        values.append((url, _number(attrs.get('ApproximateNumberOfMessagesNotVisible'),
                                    'in-flight message count'), None))
    return maximum(values, 'SQSQueue', 'sqs:GetQueueAttributes')


def queue_name_length(ctx):
    values = [(url, len(name), None) for url, name in queues(ctx).items()]
    return maximum(values, 'SQSQueue', 'sqs:ListQueues')


def _tags(url, ctx):
    tags = ctx.call(SQS, 'list_queue_tags', QueueUrl=url).get('Tags') or {}
    if not isinstance(tags, dict):
        raise NoData('SQS queue has an invalid tag inventory')
    for key, value in tags.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise NoData('SQS queue has an invalid tag')
    return tags


def _tag_maximum(measure):
    def check(ctx):
        values = [(url, measure(_tags(url, ctx)), None) for url in queues(ctx)]
        return maximum(values, 'SQSQueue', 'sqs:ListQueueTags')
    return check


def _utf8_length(values):
    return max((len(value.encode('utf-8')) for value in values), default=0)


CHECKS = [
    ('L-C491D5A4', 'In-flight messages per standard queue', in_flight_messages),
    ('L-B2A3B9D5', 'Message invisibility period',
     _attribute_maximum('VisibilityTimeout', 'visibility timeout')),
    ('L-2DA3E3B2', 'Message retention time',
     _attribute_maximum('MessageRetentionPeriod', 'message retention period')),
    ('L-49DA5CEC', 'Message size',
     _attribute_maximum('MaximumMessageSize', 'maximum message size')),
    ('L-A7816957', 'Queue delivery delay',
     _attribute_maximum('DelaySeconds', 'delivery delay')),
    ('L-E8A9C91E', 'Queue name length', queue_name_length),
    ('L-BBEFA6CF', 'Queue policy size', _policy_size),
    ('L-9F628B95', 'Statements per queue policy',
     _policy_maximum(lambda policy: len(_statements(policy)))),
    ('L-79B6240C', 'Actions per queue policy',
     _policy_maximum(lambda policy: sum(
         len(_as_list(statement.get('Action'))) + len(_as_list(statement.get('NotAction')))
         for statement in _statements(policy)))),
    ('L-6A03DCE9', 'Conditions per queue policy',
     _policy_maximum(lambda policy: sum(
         _conditions(statement) for statement in _statements(policy)))),
    ('L-F61F33C3', 'Principals per queue policy',
     _policy_maximum(lambda policy: sum(
         _principals(statement) for statement in _statements(policy)))),
    ('L-4BE1B2BD', 'Tags per queue', _tag_maximum(len)),
    ('L-A01B4DF0', 'UTF-8 queue tag key length',
     _tag_maximum(lambda tags: _utf8_length(tags))),
    ('L-BF2A6161', 'UTF-8 queue tag value length',
     _tag_maximum(lambda tags: _utf8_length(tags.values()))),
]


def get_current_quotastatus_sqs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'sqs' for service, _ in context.quotas):
        return []
    return context.run('sqs', CHECKS, skip)
