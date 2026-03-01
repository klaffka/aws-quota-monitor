import boto3
import time
import json
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_limit(sq_client, quota_code):
    """Get the applied quota limit from Service Quotas API."""
    resp = sq_client.get_service_quota(ServiceCode='lambda', QuotaCode=quota_code)
    return resp['Quota']['Value']


def _fetch_all_limits(sq_client, service_code='lambda'):
    """Batch-fetch all quota limits for a service via ListServiceQuotas.

    Returns a dict mapping QuotaCode → applied Value.
    This replaces many individual GetServiceQuota calls with a single
    paginated list call, avoiding TooManyRequestsException.
    """
    limits = {}
    try:
        paginator = sq_client.get_paginator('list_service_quotas')
        for page in paginator.paginate(ServiceCode=service_code):
            for q in page.get('Quotas', []):
                limits[q['QuotaCode']] = q['Value']
    except Exception as e:
        logger.warning(f"Failed to batch-fetch limits for {service_code}: {e}")
    return limits


def _build_entry(account_id, region, collected_at, *,
                 quota_code, quota_name, limit_value, usage_value,
                 unit='Count', collector_type='REGION_TOTAL',
                 data_source='', calculation_method='REGION_TOTAL',
                 max_resource_type=None, max_resource_id=None,
                 max_resource_meta=None):
    """Build a standardised quota entry dict."""
    utilization_pct = round(usage_value / limit_value * 100, 2) if limit_value > 0 else 0
    return {
        'PK': f"QUOTA#{account_id}#lambda#{quota_code}",
        'SK': f"TS#{collected_at}",
        'accountId': account_id,
        'region': region,
        'serviceCode': 'lambda',
        'quotaCode': quota_code,
        'quotaName': quota_name,
        'scopeType': 'ACCOUNT_REGION',
        'limitValue': limit_value,
        'usageValue': usage_value,
        'utilizationPct': utilization_pct,
        'unit': unit,
        'collectorType': collector_type,
        'dataSource': data_source,
        'calculationMethod': calculation_method,
        'maxResourceType': max_resource_type,
        'maxResourceId': max_resource_id,
        'maxResourceMeta': max_resource_meta,
        'collectedAt': collected_at,
        'ttl': int(time.time()) + 64 * 24 * 3600  # 64 days TTL
    }


# ── Main entry point ──────────────────────────────────────────────────────

def get_current_quotastatus_lambda(session=None):
    """Collect quota usage for AWS Lambda (service code: lambda).

    Returns a list of quota entry dicts ready for DynamoDB storage.
    Only quotas whose usage can be measured via API are included.
    Rate-based, per-invocation, and runtime quotas are skipped.
    """
    lambda_quotas = []
    if session is None:
        session = boto3.Session()

    collected_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    account_id = session.client('sts').get_caller_identity().get('Account')
    region = session.region_name
    lam = session.client('lambda')
    sq = session.client('service-quotas')

    # ── Batch-fetch all Lambda quota limits (single paginated call) ──
    limits = _fetch_all_limits(sq, 'lambda')
    def get_limit(quota_code):
        """Look up limit from pre-fetched map, fall back to individual API call."""
        if quota_code in limits:
            return limits[quota_code]
        return _get_limit(sq, quota_code)

    # ── Pre-fetch all functions (paginated) ───────────────────────────
    logger.info("Lambda collector: fetching function inventory")
    functions = []
    paginator = lam.get_paginator('list_functions')
    for page in paginator.paginate():
        functions.extend(page.get('Functions', []))

    logger.info(f"Lambda collector: {len(functions)} functions discovered")

    # Shorthand
    def entry(**kw):
        return _build_entry(account_id, region, collected_at, **kw)

    # ══════════════════════════════════════════════════════════════════
    #  ACCOUNT-LEVEL CHECKS
    # ══════════════════════════════════════════════════════════════════

    # L-2ACBD22F  Function and layer storage (default 75 GB)
    try:
        acct = lam.get_account_settings()
        total_code_size_limit = acct['AccountLimit']['TotalCodeSize']
        total_code_size_used = acct['AccountUsage']['TotalCodeSize']
        # Override with Service Quotas value if available (may be increased)
        try:
            sq_limit = get_limit('L-2ACBD22F')
            # Service Quotas returns in GB, API returns bytes
            if sq_limit < 1_000_000:
                total_code_size_limit = int(sq_limit * 1_073_741_824)  # GB → bytes
            else:
                total_code_size_limit = int(sq_limit)
        except Exception:
            pass  # keep GetAccountSettings value
        # Convert to GB for readability
        usage_gb = round(total_code_size_used / 1_073_741_824, 2)
        limit_gb = round(total_code_size_limit / 1_073_741_824, 2)
        lambda_quotas.append(entry(
            quota_code='L-2ACBD22F',
            quota_name='Function and layer storage',
            limit_value=limit_gb, usage_value=usage_gb,
            unit='Gigabytes',
            collector_type='ACCOUNT_TOTAL', calculation_method='ACCOUNT_TOTAL',
            data_source='lambda:GetAccountSettings'))
    except Exception as e:
        logger.warning(f"Lambda check L-2ACBD22F failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  PER-FUNCTION CHECKS  (report function with highest usage)
    # ══════════════════════════════════════════════════════════════════

    # L-75F48B05  Deployment package size – direct upload (default 50 MB)
    try:
        limit = get_limit('L-75F48B05')
        func_sizes = {}
        for fn in functions:
            func_sizes[fn['FunctionName']] = fn.get('CodeSize', 0)
        if func_sizes:
            max_fn = max(func_sizes, key=func_sizes.get)
            max_size = func_sizes[max_fn]
        else:
            max_fn, max_size = None, 0
        # Convert to MB for readability
        usage_mb = round(max_size / 1_048_576, 2)
        limit_mb = round(limit / 1_048_576, 2) if limit > 1_000 else limit
        lambda_quotas.append(entry(
            quota_code='L-75F48B05',
            quota_name='Deployment package size (direct upload)',
            limit_value=limit_mb, usage_value=usage_mb,
            unit='Megabytes',
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='Function', max_resource_id=max_fn,
            data_source='lambda:ListFunctions'))
    except Exception as e:
        logger.warning(f"Lambda check L-75F48B05 failed: {e}")

    # L-01237738  Function layers (default 5 per function)
    try:
        limit = get_limit('L-01237738')
        func_layers = {}
        for fn in functions:
            func_layers[fn['FunctionName']] = len(fn.get('Layers', []))
        if func_layers:
            max_fn = max(func_layers, key=func_layers.get)
            max_layers = func_layers[max_fn]
        else:
            max_fn, max_layers = None, 0
        lambda_quotas.append(entry(
            quota_code='L-01237738',
            quota_name='Function layers',
            limit_value=limit, usage_value=max_layers,
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='Function', max_resource_id=max_fn,
            data_source='lambda:ListFunctions'))
    except Exception as e:
        logger.warning(f"Lambda check L-01237738 failed: {e}")

    # L-6581F036  Environment variable size (default 4 KB per function)
    try:
        limit = get_limit('L-6581F036')
        func_env_sizes = {}
        for fn in functions:
            env_vars = fn.get('Environment', {}).get('Variables', {})
            # Total size = sum of key lengths + value lengths
            env_size = sum(len(k) + len(v) for k, v in env_vars.items())
            func_env_sizes[fn['FunctionName']] = env_size
        if func_env_sizes:
            max_fn = max(func_env_sizes, key=func_env_sizes.get)
            max_env_size = func_env_sizes[max_fn]
        else:
            max_fn, max_env_size = None, 0
        # Convert to KB
        usage_kb = round(max_env_size / 1024, 2)
        limit_kb = round(limit / 1024, 2) if limit > 1000 else limit
        lambda_quotas.append(entry(
            quota_code='L-6581F036',
            quota_name='Environment variable size',
            limit_value=limit_kb, usage_value=usage_kb,
            unit='Kilobytes',
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='Function', max_resource_id=max_fn,
            data_source='lambda:ListFunctions'))
    except Exception as e:
        logger.warning(f"Lambda check L-6581F036 failed: {e}")

    # L-07A00131  Function resource-based policy (default 20 KB)
    try:
        limit = get_limit('L-07A00131')
        func_policy_sizes = {}
        for fn in functions:
            try:
                policy_resp = lam.get_policy(FunctionName=fn['FunctionName'])
                policy_str = policy_resp.get('Policy', '{}')
                func_policy_sizes[fn['FunctionName']] = len(policy_str.encode('utf-8'))
            except lam.exceptions.ResourceNotFoundException:
                # No policy attached → 0 bytes
                func_policy_sizes[fn['FunctionName']] = 0
            except Exception:
                pass
        if func_policy_sizes:
            max_fn = max(func_policy_sizes, key=func_policy_sizes.get)
            max_policy_size = func_policy_sizes[max_fn]
        else:
            max_fn, max_policy_size = None, 0
        # Convert to KB
        usage_kb = round(max_policy_size / 1024, 2)
        limit_kb = round(limit / 1024, 2) if limit > 1000 else limit
        lambda_quotas.append(entry(
            quota_code='L-07A00131',
            quota_name='Function resource-based policy',
            limit_value=limit_kb, usage_value=usage_kb,
            unit='Kilobytes',
            collector_type='PER_RESOURCE_MAX', calculation_method='PER_RESOURCE_MAX',
            max_resource_type='Function', max_resource_id=max_fn,
            data_source='lambda:GetPolicy'))
    except Exception as e:
        logger.warning(f"Lambda check L-07A00131 failed: {e}")

    # L-C952DDE4  Kafka Event Source Mappings in default mode on Lambda Managed Instances
    try:
        limit = get_limit('L-C952DDE4')
        esms = []
        esm_paginator = lam.get_paginator('list_event_source_mappings')
        for page in esm_paginator.paginate():
            esms.extend(page.get('EventSourceMappings', []))
        kafka_esms = [e for e in esms
                      if 'kafka' in e.get('EventSourceArn', '').lower()
                      or e.get('SelfManagedEventSource')]
        lambda_quotas.append(entry(
            quota_code='L-C952DDE4',
            quota_name='Kafka Event Source Mappings in default mode on Lambda Managed Instances',
            limit_value=limit, usage_value=len(kafka_esms),
            collector_type='ACCOUNT_TOTAL', calculation_method='ACCOUNT_TOTAL',
            data_source='lambda:ListEventSourceMappings'))
    except Exception as e:
        logger.warning(f"Lambda check L-C952DDE4 failed: {e}")

    # ══════════════════════════════════════════════════════════════════
    #  SKIPPED QUOTAS  (not implemented in collector)
    # ══════════════════════════════════════════════════════════════════
    #
    # Covered by Reporting via official CloudWatch UsageMetric:
    #   L-B99A9384  Concurrent executions (AWS/Lambda, ConcurrentExecutions)
    #     → Reporting fetches this via get_metric_data; returns 0 if no data.
    #
    # Rate limits (TPS) – can't be measured as resource counts:
    #   L-A723F9CC  Async invocation request throughput (Lambda Managed Instances)
    #   L-A1AFA3CF  Concurrency scaling rate
    #   L-7E8754C7  DynamoDB ESM throughput (Lambda Managed Instances)
    #   L-2713A7D4  Kafka ESM throughput (Lambda Managed Instances)
    #   L-2EBBB6B4  Kinesis ESM throughput (Lambda Managed Instances)
    #   L-0A4FC1E6  SQS ESM throughput (Lambda Managed Instances)
    #   L-B2AA0F47  Rate of control plane API requests
    #   L-37540937  Rate of GetFunction API requests
    #   L-4273958C  Rate of GetPolicy API requests
    #   L-DF87A8A6  Rate of CheckpointDurableExecution API requests
    #   L-9B52FC60  Rate of GetDurableExecution API requests
    #   L-BA29C22B  Rate of GetDurableExecutionHistory API requests
    #   L-50EA21A9  Rate of GetDurableExecutionState API requests
    #   L-6A3611ED  Rate of ListDurableExecutionsByFunction API requests
    #   L-88CBC2FA  Rate of SendDurableExecutionCallbackFailure API requests
    #   L-133D658A  Rate of SendDurableExecutionCallbackHeartbeat API requests
    #   L-B82A30EA  Rate of SendDurableExecutionCallbackSuccess API requests
    #   L-4C4550DE  Rate of StopDurableExecution API requests
    #
    # Configuration limits (not capacity – using max timeout is intentional):
    #   L-9FEEFFC0  Function timeout (900 seconds)
    #
    # Per-invocation static limits:
    #   L-7C0F49F9  Asynchronous payload (256 KB)
    #   L-5C4B2C97  Synchronous payload (6 MB)
    #
    # Runtime / OS limits:
    #   L-438DAE3B  File descriptors (1024)
    #   L-77C8EE9D  Processes and threads (1024)
    #
    # Console-only:
    #   L-8E39F3F1  Deployment package size – console editor (3 MB)
    #   L-AD930C90  Test events – console editor (10)
    #
    # Unzipped size not available via API:
    #   L-E49FF7B8  Deployment package size – unzipped (250 MB)
    #
    # Durable executions (newer feature, mostly per-execution limits):
    #   L-560437FE  Durable execution storage written in megabytes
    #   L-A0D6E196  Function invocation rate to initiate durable executions
    #   L-42D0A120  Max durable operations per durable execution
    #   L-ABBF0CF3  Maximum running durable executions
    #
    # Misc:
    #   L-F864D568  Capacity providers

    logger.info(f"Lambda collector: completed with {len(lambda_quotas)} quota entries")
    return lambda_quotas