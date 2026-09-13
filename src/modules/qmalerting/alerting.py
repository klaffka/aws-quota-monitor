"""Durable alert transitions protected by a DynamoDB lease and observation ordering."""
import json
import os
import time
from uuid import uuid4
from botocore.exceptions import ClientError
from modules.qmcore.aws import CONFIG
from modules.qmcore.model import number, valid_measurement
from modules.qmdb.db import QuotaLogDb


class AlertBusy(RuntimeError):
    pass


class QuotaAlert:
    def __init__(self, session, sns_topic_arn=None, threshold_pct=80, db=None, clock=time.time):
        threshold = number(threshold_pct)
        if threshold is None or not 0 < threshold <= 100:
            raise ValueError('QM_ALERT_THRESHOLD must be greater than 0 and at most 100')
        self.threshold_pct = threshold
        self.sns_topic_arn = sns_topic_arn or os.getenv('QM_ALERT_TOPIC_ARN')
        self.sns_client = session.client('sns', config=CONFIG)
        self.db = db or QuotaLogDb(session)
        self.clock = clock

    def check_and_alert(self, quota):
        if not self.sns_topic_arn or not valid_measurement(quota):
            return False
        key = {'PK': f"ALERT#{quota['accountId']}#{quota['region']}#{quota['serviceCode']}#{quota['quotaCode']}", 'SK': 'STATE'}
        table, token, now = self.db.table, uuid4().hex, int(self.clock())
        try:
            response = table.update_item(Key=key,
                UpdateExpression='SET leaseToken = :token, leaseUntil = :until',
                ConditionExpression='attribute_not_exists(leaseUntil) OR leaseUntil < :now',
                ExpressionAttributeValues={':token': token, ':until': now + 1000, ':now': now},
                ReturnValues='ALL_NEW')
        except ClientError as exc:
            if exc.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise AlertBusy('Another invocation holds the alert lease') from exc
            raise
        state = response['Attributes']
        try:
            observed = quota['collectedAt']
            if observed <= state.get('lastObservedAt', ''):
                self._release(key, token)
                return False
            utilization = float(quota['usageValue']) / float(quota['limitValue']) * 100
            breached = utilization >= self.threshold_pct
            previous = state.get('alarmState', 'OK')
            kind = None
            if breached:
                if previous != 'ALARM':
                    kind = 'BREACH'
                elif now - int(state.get('lastSentAt', 0)) >= 86400:
                    kind = 'REMINDER'
            elif previous == 'ALARM':
                kind = 'RECOVERY'
            if kind:
                # Only commit the new state after SNS accepted the publication.
                self.sns_client.publish(TopicArn=self.sns_topic_arn,
                    Subject=f"Quota {kind}: {quota['serviceCode']} {quota['quotaCode']}"[:100],
                    Message=json.dumps({'event': kind, 'thresholdPct': self.threshold_pct,
                                        'quota': quota}, default=str))
            values = {':token': token, ':observed': observed, ':state': 'ALARM' if breached else 'OK'}
            expression = 'SET lastObservedAt = :observed, alarmState = :state'
            if kind:
                expression += ', lastSentAt = :sent'
                values[':sent'] = int(self.clock())
            table.update_item(Key=key, UpdateExpression=expression + ' REMOVE leaseToken, leaseUntil',
                              ConditionExpression='leaseToken = :token', ExpressionAttributeValues=values)
            return bool(kind)
        except Exception:
            self._release(key, token)
            raise

    def _release(self, key, token):
        self.db.table.update_item(Key=key, UpdateExpression='REMOVE leaseToken, leaseUntil',
                                  ConditionExpression='leaseToken = :token',
                                  ExpressionAttributeValues={':token': token})
