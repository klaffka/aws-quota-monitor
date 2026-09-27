import os
import random
import time
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from modules.qmcore.aws import CONFIG


class QuotaLogDb:
    def __init__(self, session, table_name=None, region_name=None):
        self.dynamodb = session.resource('dynamodb', region_name=region_name or session.region_name,
                                        config=CONFIG)
        self.table = self.dynamodb.Table(table_name or os.getenv('QM_QUOTA_TABLE', 'qm-quotalog'))

    def _to_dynamodb_compatible(self, value):
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, dict):
            return {k: self._to_dynamodb_compatible(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._to_dynamodb_compatible(v) for v in value]
        return value

    def get_latest_quota_entry(self, pk):
        return next(iter(self.table.query(KeyConditionExpression=Key('PK').eq(pk),
                                         ScanIndexForward=False, Limit=1).get('Items', [])), None)

    def put_quota_entry(self, quota_entry):
        self.table.put_item(Item=self._to_dynamodb_compatible(quota_entry))

    def put_quota_entries(self, entries):
        """Yield (entry, error) only after its write is confirmed or abandoned.

        Retry only unprocessed items, with bounded backoff. Unknown outcomes
        never authorize alerts. Keep duplicate keys in separate requests.
        """
        batch, keys = [], set()
        for entry in entries:
            key = (entry['PK'], entry['SK'])
            if batch and (len(batch) == 25 or key in keys):
                yield from self._write_batch(batch)
                batch, keys = [], set()
            batch.append(entry)
            keys.add(key)
        if batch:
            yield from self._write_batch(batch)

    def _write_batch(self, entries):
        pending = []
        for entry in entries:
            try:
                item = self._to_dynamodb_compatible(entry)
                pending.append((entry, {'PutRequest': {'Item': item}}))
            except Exception as exc:
                yield entry, str(exc)
        for attempt in range(5):
            if not pending:
                return
            try:
                response = self.table.meta.client.batch_write_item(
                    RequestItems={self.table.name: [request for _, request in pending]})
                unprocessed = response.get('UnprocessedItems', {}).get(self.table.name, [])
                keys = {(r['PutRequest']['Item']['PK'], r['PutRequest']['Item']['SK'])
                        for r in unprocessed}
            except Exception as exc:
                for entry, _ in pending:
                    yield entry, str(exc)
                return
            remaining = []
            for entry, request in pending:
                if (entry['PK'], entry['SK']) in keys:
                    remaining.append((entry, request))
                else:
                    yield entry, None
            pending = remaining
            if pending and attempt < 4:
                time.sleep(random.uniform(0, 0.1 * 2 ** attempt))
        for entry, _ in pending:
            yield entry, 'DynamoDB batch write remained unprocessed after 5 attempts'

    def get_quota_entry(self, pk, sk):
        return self.table.get_item(Key={'PK': pk, 'SK': sk}, ConsistentRead=True).get('Item')
