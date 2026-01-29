import boto3
import sys
from qmchecks.ec2.ec2 import get_current_quotastatus_ec2
from qmdb.db import QuotaLogDb
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):  
    # check event type 
    session = boto3.Session(profile_name='BA')
    client = session.client('service-quotas')
    db = QuotaLogDb(session=session, table_name='qm-quotalog')
    current_quota = get_current_quotastatus_ec2(session=session)
    for quota in current_quota:
        pk = f"QUOTA#{quota['accountId']}#{quota['region']}#quota#{quota['quotaCode']}"
        sk = f"TS#{quota['collectedAt']}"
        quota_entry = {
            'PK': pk,
            'SK': sk,
            'accountId': quota['accountId'],
            'region': quota['region'],
            'serviceCode': quota['serviceCode'],
            'quotaCode': quota['quotaCode'],
            'quotaName': quota['quotaName'],
            'scopeType': quota['scopeType'],
            'limitValue': quota['limitValue'],
            'usageValue': quota['usageValue'],
            'utilizationPct': quota['utilizationPct'],
            'unit': quota['unit'],
            'collectorType': quota['collectorType'],
            'dataSource': quota['dataSource'],
            'calculationMethod': quota['calculationMethod'],
            'maxResourceType': quota['maxResourceType'],
            'maxResourceId': quota['maxResourceId'],
            'maxResourceMeta': quota['maxResourceMeta'],
            'collectedAt': quota['collectedAt'],
            'ttl': quota['ttl']
        }
        db.put_quota_entry(quota_entry)
        db.update_latest_quota_entry(pk, sk)
        logger.info(f"Stored quota entry for {pk} with SK {sk}")
    #print(f"Quota utilization report completed: {response['Quotas']}")
    return {"statusCode": 200, "body": f"Current EC2 quota: {current_quota}"}


if __name__ == "__main__":
    sys.exit(lambda_handler({}, {}))