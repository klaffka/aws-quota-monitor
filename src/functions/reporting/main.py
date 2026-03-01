import boto3
import os
import csv
import json
import time
from io import StringIO
from datetime import datetime, timedelta
from modules.qmdb.db import QuotaLogDb
import logging
from botocore.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Generate quota utilization report as CSV and upload to S3
    """
    profile = os.environ.get('QM_AWS_PROFILE') or os.environ.get('AWS_PROFILE')
    if profile:
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3.Session()
    
    # Get configuration
    s3_bucket = os.environ.get('QM_REPORT_BUCKET')
    if not s3_bucket:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "QM_REPORT_BUCKET environment variable not set"})
        }
    
    days_back = int(event.get('days_back', os.environ.get('QM_REPORT_DAYS', '30')))
    
    logger.info(f"Generating report for last {days_back} days to S3://{s3_bucket}")
    
    # Initialize clients
    s3_client = session.client('s3')
    sqs_client = session.client(
        'service-quotas',
        config=Config(
            retries={'max_attempts': 10, 'mode': 'adaptive'},
            max_pool_connections=20
        )
    )
    db = QuotaLogDb(session=session, table_name='qm-quotalog')
    
    # Fetch all Service Quotas
    all_quotas = fetch_all_service_quotas(sqs_client)
    logger.info(f"Fetched {len(all_quotas)} service quotas")
    
    # Enrich with CloudWatch (metric quotas) and DynamoDB (non-metric quotas)
    enriched_quotas = enrich_quotas_with_db(all_quotas, db, days_back, session)
    
    # Generate CSV
    csv_content = generate_csv_report(enriched_quotas)
    
    # Upload to S3
    report_date = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    s3_key = f"reports/quota-report-{report_date}.csv"
    
    try:
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=csv_content,
            ContentType='text/csv'
        )
        logger.info(f"Report uploaded to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to upload to S3: {str(e)}"})
        }
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Report generated successfully",
            "s3_location": f"s3://{s3_bucket}/{s3_key}",
            "quotas_count": len(enriched_quotas)
        })
    }


def fetch_all_service_quotas(client):
    """Fetch all service quotas.

    The Service Quotas API requires a ServiceCode when listing quotas, so first
    list available services and then paginate quotas for each service.
    Relies on botocore adaptive retry mode (configured on the client) to handle
    rate limiting automatically — no custom retry loop needed.
    """
    quotas = []

    try:
        # Step 1: collect all service codes
        service_codes = []
        services_paginator = client.get_paginator('list_services')
        for svc_page in services_paginator.paginate():
            for svc in svc_page.get('Services', []):
                code = svc.get('ServiceCode')
                if code:
                    service_codes.append(code)

        logger.info(f"Discovered {len(service_codes)} services via list_services")

        if not service_codes:
            logger.warning("No services discovered; returning empty quotas list")
            return []

        # Step 2: list quotas per service (adaptive retry handles rate limiting)
        for i, service_code in enumerate(service_codes):
            try:
                quotas_paginator = client.get_paginator('list_service_quotas')
                service_quota_count = 0
                for page in quotas_paginator.paginate(ServiceCode=service_code):
                    if 'Quotas' in page:
                        quotas.extend(page['Quotas'])
                        service_quota_count += len(page['Quotas'])
                logger.info(f"[{i+1}/{len(service_codes)}] {service_code}: {service_quota_count} quotas")
            except Exception as e:
                logger.warning(f"[{i+1}/{len(service_codes)}] Failed {service_code}: {e}")
            # Small delay between services to stay under rate limit
            time.sleep(0.3)

    except Exception as e:
        logger.error(f"Error fetching service list or quotas: {e}")

    logger.info(f"Total quotas discovered: {len(quotas)}")
    return quotas


def enrich_quotas_with_db(quotas, db, days_back, session):
    """
    Enrich quotas with max usage from the reporting period.

    Strategy:
    1. Quotas WITH UsageMetric → CloudWatch get_metric_data (batch, cheap)
    2. Quotas WITHOUT UsageMetric → DynamoDB scan (custom collector data)
    3. No metric and no DB data → "NOT SUPPORTED"
    """
    # Split quotas into metric vs non-metric
    metric_quotas = [q for q in quotas if q.get('UsageMetric')]
    non_metric_quotas = [q for q in quotas if not q.get('UsageMetric')]
    logger.info(f"Quotas split: {len(metric_quotas)} with CloudWatch metric, {len(non_metric_quotas)} without")

    # 1) CloudWatch for metric quotas (batch query, 1 datapoint per quota)
    cw_usage = fetch_cloudwatch_max_usage(session, metric_quotas, days_back)
    logger.info(f"CloudWatch returned usage for {len(cw_usage)} quotas")

    # 2) DynamoDB only for non-metric quotas
    cutoff_date = 'TS#' + (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
    db_usage_map = build_usage_max_map(db, cutoff_date)
    logger.info(f"DynamoDB returned usage for {len(db_usage_map)} quotas")

    enriched = []
    for quota in quotas:
        service_code = quota.get('ServiceCode')
        quota_code = quota.get('QuotaCode')
        quota_name = quota.get('QuotaName')
        applied_value = quota.get('Value')  # from Service Quotas API

        if quota.get('UsageMetric'):
            # CloudWatch path
            cw_val = cw_usage.get((service_code, quota_code))
            status = cw_val if cw_val is not None else 0
            usage_source = 'official_metric'
        else:
            # DynamoDB path
            db_entry = db_usage_map.get((service_code, quota_code))
            if db_entry is not None:
                status = db_entry['max_usage']
                applied_value = db_entry.get('limit_value') or applied_value
                usage_source = 'collector_implementation'
            else:
                status = "NOT SUPPORTED"
                usage_source = 'not_supported'

        enriched.append({
            'quotaName': quota_name,
            'serviceCode': service_code,
            'quotaCode': quota_code,
            'appliedValue': applied_value,
            'maxUsage': status,
            'usageSource': usage_source
        })

    return enriched


def fetch_cloudwatch_max_usage(session, metric_quotas, days_back):
    """
    Batch-query CloudWatch for max usage of quotas with UsageMetric.

    Uses get_metric_data with up to 500 metrics per call.
    Period = entire reporting window → 1 datapoint per metric = minimal cost.
    """
    if not metric_quotas:
        return {}

    cw_client = session.client('cloudwatch')
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)
    # Entire period as one datapoint; must be multiple of 60
    period = max(60, days_back * 86400)
    period = period - (period % 60)  # round down to multiple of 60

    usage_map = {}
    batch_size = 500  # CloudWatch limit per get_metric_data call

    for batch_start in range(0, len(metric_quotas), batch_size):
        batch = metric_quotas[batch_start:batch_start + batch_size]
        queries = []
        id_to_key = {}

        for i, quota in enumerate(batch):
            metric = quota['UsageMetric']
            query_id = f"m{batch_start + i}"

            # Convert MetricDimensions dict to CloudWatch Dimensions list
            dims = [
                {'Name': k, 'Value': v}
                for k, v in metric.get('MetricDimensions', {}).items()
            ]

            queries.append({
                'Id': query_id,
                'MetricStat': {
                    'Metric': {
                        'Namespace': metric.get('MetricNamespace', 'AWS/Usage'),
                        'MetricName': metric.get('MetricName', 'ResourceCount'),
                        'Dimensions': dims
                    },
                    'Period': period,
                    'Stat': 'Maximum'
                },
                'ReturnData': True
            })
            id_to_key[query_id] = (quota['ServiceCode'], quota['QuotaCode'])

        try:
            # Handle pagination (NextToken)
            next_token = None
            while True:
                kwargs = {
                    'MetricDataQueries': queries,
                    'StartTime': start_time,
                    'EndTime': end_time
                }
                if next_token:
                    kwargs['NextToken'] = next_token

                response = cw_client.get_metric_data(**kwargs)

                for result in response.get('MetricDataResults', []):
                    query_id = result['Id']
                    values = result.get('Values', [])
                    if values:
                        key = id_to_key[query_id]
                        usage_map[key] = max(values)

                next_token = response.get('NextToken')
                if not next_token:
                    break

            logger.info(f"CloudWatch batch {batch_start // batch_size + 1}: "
                        f"{len(batch)} metrics queried, {sum(1 for r in response.get('MetricDataResults', []) if r.get('Values'))} with data")
        except Exception as e:
            logger.warning(f"CloudWatch batch query failed (batch {batch_start // batch_size + 1}): {e}")

    return usage_map


def build_usage_max_map(db, cutoff_date):
    """Scan DynamoDB once and build a (service_code, quota_code) -> {max_usage, limit_value} map."""
    usage_map = {}
    total_scanned = 0
    try:
        scan_kwargs = {
            'FilterExpression': 'attribute_exists(usageValue) AND #sk >= :cutoff',
            'ExpressionAttributeNames': {'#sk': 'SK'},
            'ExpressionAttributeValues': {':cutoff': cutoff_date}
        }

        while True:
            response = db.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            total_scanned += len(items)
            for item in items:
                service_code = item.get('serviceCode')
                quota_code = item.get('quotaCode')
                if not service_code or not quota_code:
                    logger.debug(f"Skipping item without serviceCode/quotaCode: PK={item.get('PK')}")
                    continue
                val = item.get('usageValue')
                if val is not None:
                    try:
                        val_f = float(val)
                    except (ValueError, TypeError):
                        continue
                    key = (service_code, quota_code)
                    existing = usage_map.get(key)
                    if existing is None or val_f > existing.get('max_usage', -1):
                        limit_val = item.get('limitValue')
                        try:
                            limit_f = float(limit_val) if limit_val is not None else None
                        except (ValueError, TypeError):
                            limit_f = None
                        usage_map[key] = {
                            'max_usage': val_f,
                            'limit_value': limit_f
                        }

            last_evaluated = response.get('LastEvaluatedKey')
            if not last_evaluated:
                break
            scan_kwargs['ExclusiveStartKey'] = last_evaluated
    except Exception as e:
        logger.warning(f"Error scanning DynamoDB for usage map: {e}")

    logger.info(f"DynamoDB scan: {total_scanned} items scanned, {len(usage_map)} unique quotas with usage")
    return usage_map


def generate_csv_report(quotas):
    """Generate CSV from quota data"""
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['Quota Name', 'Service', 'Quota Code', 'Applied Value', 'Max Usage (Current Month)', 'Usage Source']
    )
    
    writer.writeheader()
    for quota in quotas:
        writer.writerow({
            'Quota Name': quota.get('quotaName', 'N/A'),
            'Service': quota.get('serviceCode', 'N/A'),
            'Quota Code': quota.get('quotaCode', 'N/A'),
            'Applied Value': quota.get('appliedValue', 'N/A'),
            'Max Usage (Current Month)': quota.get('maxUsage', 'NOT SUPPORTED'),
            'Usage Source': quota.get('usageSource', 'unknown')
        })
    
    return output.getvalue()


if __name__ == "__main__":
    test_event = {"days_back": 30}
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
