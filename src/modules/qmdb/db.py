import boto3
from decimal import Decimal

#DynamoDB Klasse zur verwaltung von Quota Einträgen
class QuotaLogDb:
    def __init__(self, session, table_name, region_name='eu-central-1'):
        self.dynamodb = session.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    # Konvertiert Werte in ein DynamoDB-kompatibles Format (Decimal für float)
    def _to_dynamodb_compatible(self, value):
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, dict):
            return {k: self._to_dynamodb_compatible(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._to_dynamodb_compatible(v) for v in value]
        return value

    # Holt den neuesten Quota Eintrag basierend auf dem PK
    def get_latest_quota_entry(self, pk):
        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(pk),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get('Items', [])
        if items:
            return items[0]
        return None
    
    # Fügt einen neuen Quota Eintrag in die Tabelle ein
    def put_quota_entry(self, quota_entry):
        quota_entry = self._to_dynamodb_compatible(quota_entry)
        self.table.put_item(Item=quota_entry)

    # Holt einen spezifischen Quota Eintrag basierend auf PK und SK
    def get_quota_entry(self, pk, sk):
        response = self.table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        return response.get('Item', None)

"""
DynamoDB Beispiel Eintrag:
PK: QUOTA#AccountID#Region#quota#id
SK: TS#Timestamp (Aktuellster eintrag bekommt LATEST statt Timestamp, muss dann aber aktualisiert werden)
accountId: AccountID
region: Region
serviceCode: der Service Code, z.B. ec2
quotaCode: Quota Code, z.B. AMI_SHARING
quotaName: Name der Quota, z.B. AMI sharing
scopeType: SCOPE_TYPE, z.B. ACCOUNT_REGION oder ORGANIZATION
limitValue: Limit Wert der Quota, z.B. 1000
usageValue: Aktueller Nutzungswert der Quota, z.B. 812
utilizationPct: Auslastung in Prozent, z.B. 81.2
unit: Einheit der Quota, z.B. Count
maxResourceType: Maximaler Ressourcentyp, z.B. AMI
maxResourceId: ID der Ressource mit dem maximalen Wert, z.B. ami-0123456789abcdef0
maxResourceMeta: Metadaten zur Ressource, z.B. {"breakdown": {"accounts": 800, "organizations": 1, "organizationalUnits": 11, "public": 0}}
collectorType: Art des Collectors, z.B. PER_RESOURCE_MAX
dataSource: Datenquelle, z.B. service-quotas + ec2:DescribeImageAttribute
calculationMethod: Berechnungsmethode, z.B. MAX_PER_RESOURCE
collectedAt: Zeitpunkt der Datenerfassung, z.B. 2025-12-31T11:58:12Z
ttl: Zeit in Sekunden seit Epoch bis wann der Eintrag gültig ist, z.B. 1777415892
Beispiel Eintrag:
{
  "PK": "QUOTA#123456789012#eu-central-1#ec2#AMI_SHARING",
  "SK": "TS#2025-12-31T11:58:12Z",

  "accountId": "123456789012",
  "region": "eu-central-1",
  "serviceCode": "ec2",
  "quotaCode": "AMI_SHARING",
  "quotaName": "AMI sharing",
  "scopeType": "ACCOUNT_REGION",

  "limitValue": 1000,
  "usageValue": 812,
  "utilizationPct": 81.2,
  "unit": "Count",

  "maxResourceType": "AMI",
  "maxResourceId": "ami-0123456789abcdef0",
  "maxResourceMeta": {
    "breakdown": {
      "accounts": 800,
      "organizations": 1,
      "organizationalUnits": 11,
      "public": 0
    }
  },

  "collectorType": "PER_RESOURCE_MAX",
  "dataSource": "service-quotas + ec2:DescribeImageAttribute",
  "calculationMethod": "MAX_PER_RESOURCE",

  "collectedAt": "2025-12-31T11:58:12Z",

  "ttl": 1777415892
}
"""
