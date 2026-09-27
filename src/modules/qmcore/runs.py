"""Stable scheduled windows and leased, idempotent collector executions."""
from datetime import datetime, timedelta, UTC
from hashlib import sha256
from uuid import uuid4

from botocore.exceptions import ClientError
from modules.qmcore.model import iso, utcnow


def run_window(event, now):
    event = event or {}
    scheduled = event.get('source') in {'aws.events', 'eventbridge-scheduler'}
    raw = event.get('time')
    if (scheduled or event.get('runId')) and not raw:
        raise ValueError('Scheduled or explicitly identified runs require an original time')
    end = datetime.fromisoformat(raw.replace('Z', '+00:00')) if raw else now
    if end.tzinfo is None:
        raise ValueError('Run time must include a timezone')
    end = end.astimezone(UTC).replace(microsecond=0)
    if end > now + timedelta(minutes=5):
        raise ValueError('Run time is in the future')
    if now - end > timedelta(days=14):
        raise ValueError('Replay is limited to 14 days; use historical reporting for older windows')
    identity = str(event.get('runId') or (iso(end) if raw else uuid4().hex))
    return sha256(identity.encode()).hexdigest(), end - timedelta(days=1), end


class RunBusy(RuntimeError):
    pass


class RunLease:
    def __init__(self, db, account, region, run_id, clock=utcnow):
        self.table, self.clock = db.table, clock
        self.key = {'PK': f'EXECUTION#{account}#{region}', 'SK': run_id}
        self.token = uuid4().hex

    def acquire(self):
        now = int(self.clock().timestamp())
        try:
            self.table.update_item(Key=self.key,
                UpdateExpression='SET #state = :running, leaseToken = :token, leaseUntil = :until, #ttl = :ttl',
                ConditionExpression='(attribute_not_exists(#state) OR #state <> :complete) AND '
                                    '(attribute_not_exists(leaseUntil) OR leaseUntil < :now)',
                ExpressionAttributeNames={'#state': 'state', '#ttl': 'ttl'},
                ExpressionAttributeValues={':running': 'RUNNING', ':complete': 'COMPLETE',
                    ':token': self.token, ':until': now + 960, ':now': now, ':ttl': now + 64 * 86400})
            return True
        except ClientError as exc:
            if exc.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
            item = self.table.get_item(Key=self.key, ConsistentRead=True).get('Item', {})
            if item.get('state') == 'COMPLETE':
                return False
            raise RunBusy('Another invocation holds this run lease') from exc

    def finish(self, success):
        self.table.update_item(Key=self.key,
            UpdateExpression='SET #state = :state REMOVE leaseToken, leaseUntil',
            ConditionExpression='leaseToken = :token',
            ExpressionAttributeNames={'#state': 'state'},
            ExpressionAttributeValues={':state': 'COMPLETE' if success else 'FAILED', ':token': self.token})
