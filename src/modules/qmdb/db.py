import os
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

    def get_quota_entry(self, pk, sk):
        return self.table.get_item(Key={'PK': pk, 'SK': sk}, ConsistentRead=True).get('Item')
