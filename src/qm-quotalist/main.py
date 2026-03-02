import os
from typing import Any, Dict, Iterable, List, Optional

import boto3

"""DynamoDB Schema: Partition Key = QuotaCode (String), Sort Key = ServiceCode (String).
Each item mirrors the payload of list_service_quotas so we can rebuild the AWS view locally.
"""


def lambda_handler(event: Optional[dict], context: Any):
    """
    Lambda entry point.
    Fetches all AWS Service Quotas for the requested services,
    compares them with the current DynamoDB entries and only writes
    changes/new records. This keeps the number of DynamoDB write units low.
    """
    table_name = os.environ["DYNAMODB_TABLE"]
    service_codes = _resolve_service_codes(event)

    sq_client = boto3.client("service-quotas")
    dynamodb = _dynamodb_resource()
    table = dynamodb.Table(table_name)

    results = []
    for service_code in service_codes:
        result = _sync_service_quotas(service_code, table, sq_client)
        results.append(result)

    return {
        "statusCode": 200,
        "body": {
            "table": table_name,
            "results": results,
        },
    }


def _resolve_service_codes(event: Optional[dict]) -> List[str]:
    """Allow a comma separated env var or list via the Lambda event for flexibility."""
    if event and "serviceCodes" in event:
        requested = event["serviceCodes"]
        if isinstance(requested, str):
            return [code.strip() for code in requested.split(",") if code.strip()]
        if isinstance(requested, Iterable):
            return [str(code).strip() for code in requested if str(code).strip()]

    env_var = os.getenv("SERVICE_CODES", "ec2")
    return [code.strip() for code in env_var.split(",") if code.strip()]


def _sync_service_quotas(service_code: str, table, sq_client) -> Dict[str, int]:
    """Read the AWS quotas for one service, compare with DynamoDB and stage only the diffs."""
    quotas = list(_list_service_quotas(service_code, sq_client))
    if not quotas:
        return {"serviceCode": service_code, "new": 0, "updated": 0, "unchanged": 0}

    existing_items = _load_existing_items(table, quotas)
    new = updated = unchanged = 0

    # Batch writer prevents one-off PutItem calls and retries unprocessed items for us.
    with table.batch_writer(overwrite_by_pkeys=["QuotaCode", "ServiceCode"]) as writer:
        for quota in quotas:
            normalized = _normalize_quota(quota)
            key = _item_key(normalized)

            if existing_items.get(key) == normalized:
                unchanged += 1
                continue

            writer.put_item(Item=normalized)
            if key in existing_items:
                updated += 1
            else:
                new += 1

    return {"serviceCode": service_code, "new": new, "updated": updated, "unchanged": unchanged}


def _list_service_quotas(service_code: str, sq_client) -> Iterable[Dict]:
    """Generator around the paginator so we only keep one page of quotas in memory."""
    paginator = sq_client.get_paginator("list_service_quotas")
    for page in paginator.paginate(ServiceCode=service_code):
        yield from page.get("Quotas", [])


def _load_existing_items(table, quotas: List[Dict]) -> Dict[str, Dict]:
    """Batch read all existing quota items for comparison."""
    dynamodb_client = table.meta.client
    pending_keys = [
        {"QuotaCode": quota["QuotaCode"], "ServiceCode": quota["ServiceCode"]} for quota in quotas
    ]
    existing: Dict[str, Dict] = {}

    while pending_keys:
        batch, pending_keys = pending_keys[:100], pending_keys[100:]
        response = dynamodb_client.batch_get_item(RequestItems={table.name: {"Keys": batch}})
        items = response.get("Responses", {}).get(table.name, [])
        for item in items:
            existing[_item_key(item)] = item

        unprocessed = response.get("UnprocessedKeys", {}).get(table.name, {}).get("Keys", [])
        if unprocessed:
            pending_keys.extend(unprocessed)

    return existing


def _normalize_quota(quota: Dict) -> Dict:
    """Ensure optional fields exist so equality checks are reliable."""
    normalized = quota.copy()
    normalized.setdefault("MetricAvailable", False)
    normalized.setdefault("UsageMetric", {})
    normalized.setdefault("CustomMetric", {})
    return normalized


def _item_key(item: Dict) -> str:
    """Consistent composite key string used for dict lookups."""
    return f"{item['QuotaCode']}#{item['ServiceCode']}"


def _dynamodb_resource():
    """Create a DynamoDB resource that optionally targets a local endpoint for testing."""
    endpoint_url = os.getenv("DYNAMODB_ENDPOINT")
    if endpoint_url:
        return boto3.resource("dynamodb", endpoint_url=endpoint_url)
    return boto3.resource("dynamodb")
