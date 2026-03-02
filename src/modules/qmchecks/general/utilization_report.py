import boto3
import time

def quota_utilization_report(service_code=None, session=None):
    """Generate a quota utilization report for specified service quotas"""
    if session is None:
        session = boto3.Session()
    client = session.client('service-quotas')
    response = client.start_quota_utilization_report()
    report_id = response['ReportId']
    while response['Status'] != 'COMPLETED':
        time.sleep(1)
        response = client.get_quota_utilization_report(ReportId=report_id)
    response = client.get_quota_utilization_report(ReportId=report_id)
    return response

def process_quota_utilization_report(utalizationReport, session=None):
    """Process quota utilization report and return quota entries"""
    quotas = []
    accountId = session.client('sts').get_caller_identity().get('Account')
    
    for quota in utalizationReport['Quotas']:
        quota_entry = {
            "PK": f"QUOTA#{accountId}#{quota['ServiceCode']}#{quota['QuotaCode']}",
            "SK": f"TS#{utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "accountId": accountId,
            "region": session.region_name,
            "serviceCode": quota['ServiceCode'],
            "quotaCode": quota['QuotaCode'],
            "quotaName": quota['QuotaName'],
            "scopeType": "ACCOUNT_REGION",
            "limitValue": quota['AppliedValue'],
            "usageValue": quota['Utilization']/100 * quota['AppliedValue'] if quota['AppliedValue'] > 0 else 0,
            "utilizationPct": quota['Utilization'],
            "unit": None,
            "maxResourceType": None,
            "maxResourceId": None,
            "maxResourceMeta": None,
            "collectorType": "QUOTA_UTILIZATION_REPORT",
            "dataSource": "service-quotas: GetQuotaUtilizationReport",
            "calculationMethod": "QUOTA_UTILIZATION_REPORT",
            "collectedAt": utalizationReport['GeneratedAt'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            "ttl": int(time.time()) + 64 * 24 * 3600  # 64 days TTL
        }
        quotas.append(quota_entry)
    
    return quotas
