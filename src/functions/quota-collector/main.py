import boto3
import sys
import os
from modules.qmchecks.ec2.ec2 import get_current_quotastatus_ec2
from modules.qmchecks.vpc.vpc import get_current_quotastatus_vpc
from modules.qmchecks.lambda_checks.lambda_checks import get_current_quotastatus_lambda
from modules.qmalerting.alerting import QuotaAlert
from modules.qmdb.db import QuotaLogDb
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):  
    # check event type 
    # Allow using a local AWS profile for testing (set AWS_PROFILE or QM_AWS_PROFILE),
    # otherwise use the default session (Lambda will use its IAM role).
    profile = os.environ.get('QM_AWS_PROFILE') or os.environ.get('AWS_PROFILE')
    if profile:
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3.Session()
    
    client = session.client('service-quotas')
    db = QuotaLogDb(session=session, table_name='qm-quotalog')
    
    # Initialize alert system
    alert_threshold = int(os.environ.get('QM_ALERT_THRESHOLD', '80'))
    alert_system = QuotaAlert(session=session, threshold_pct=alert_threshold)
    
    # Get EC2-specific quotas (custom checks not covered by CloudWatch metrics)
    current_quota = get_current_quotastatus_ec2(session=session)
    
    # Get VPC-specific quotas
    vpc_quotas = get_current_quotastatus_vpc(session=session)
    current_quota.extend(vpc_quotas)
    
    # Get Lambda-specific quotas
    lambda_quotas = get_current_quotastatus_lambda(session=session)
    current_quota.extend(lambda_quotas)
    
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
        logger.info(f"Stored quota entry for {pk} with SK {sk}")
        
        # Check and send alert if threshold exceeded
        alert_system.check_and_alert(quota)
    #print(f"Quota utilization report completed: {response['Quotas']}")
    return {"statusCode": 200, "body": f"Current EC2 quota: {current_quota}"}


if __name__ == "__main__":
    sys.exit(lambda_handler({}, {}))