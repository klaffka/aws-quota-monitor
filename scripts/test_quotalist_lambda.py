#!/usr/bin/env python3
"""
Manual test harness for the qm-quotalist Lambda.

It wires the Lambda into a (local) DynamoDB instance, optionally creates the table,
and invokes lambda_handler with a user provided event. This lets you dry-run the
quota sync workflow without deploying the Lambda.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REPO_ROOT = Path(__file__).resolve().parents[1]
LAMBDA_SOURCE = REPO_ROOT / "src" / "qm-quotalist" / "main.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--table",
        required=True,
        help="Name of the DynamoDB table that stores the quotas.",
    )
    parser.add_argument(
        "--service-codes",
        nargs="+",
        default=["ec2"],
        help="Space separated list of AWS ServiceCodes to sync (e.g. ec2 iam).",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_REGION", "eu-central-1"),
        help="AWS region for the Service Quotas API and DynamoDB.",
    )
    parser.add_argument(
        "--dynamodb-endpoint",
        default=os.getenv("DYNAMODB_ENDPOINT"),
        help="Override DynamoDB endpoint (use http://localhost:8000 for DynamoDB Local).",
    )
    parser.add_argument(
        "--create-table",
        action="store_true",
        help="Create the table if it does not exist yet.",
    )
    parser.add_argument(
        "--billing-mode",
        choices=["PAY_PER_REQUEST", "PROVISIONED"],
        default="PAY_PER_REQUEST",
        help="Billing mode for a newly created table.",
    )
    parser.add_argument(
        "--read-capacity",
        type=int,
        default=5,
        help="RCU for PROVISIONED tables (ignored for PAY_PER_REQUEST).",
    )
    parser.add_argument(
        "--write-capacity",
        type=int,
        default=5,
        help="WCU for PROVISIONED tables (ignored for PAY_PER_REQUEST).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    os.environ["AWS_REGION"] = args.region
    os.environ["AWS_DEFAULT_REGION"] = args.region
    os.environ["DYNAMODB_TABLE"] = args.table
    os.environ["SERVICE_CODES"] = ",".join(args.service_codes)
    if args.dynamodb_endpoint:
        os.environ["DYNAMODB_ENDPOINT"] = args.dynamodb_endpoint

    if args.create_table:
        ensure_table(
            table=args.table,
            region=args.region,
            endpoint=args.dynamodb_endpoint,
            billing_mode=args.billing_mode,
            read_capacity=args.read_capacity,
            write_capacity=args.write_capacity,
        )

    lambda_module = load_lambda_module()
    event = {"serviceCodes": args.service_codes}
    result = lambda_module.lambda_handler(event, context=None)

    print("Lambda invocation result:")
    print(json.dumps(result, indent=2, default=str))


def ensure_table(
    table: str,
    region: str,
    endpoint: str | None,
    billing_mode: str,
    read_capacity: int,
    write_capacity: int,
) -> None:
    """Ensure DynamoDB table exists so the Lambda can write to it."""
    dynamodb = boto3.resource("dynamodb", region_name=region, endpoint_url=endpoint)
    table_ref = dynamodb.Table(table)
    try:
        table_ref.load()
        print(f"DynamoDB table '{table}' already exists")
        return
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        print(f"Creating DynamoDB table '{table}' for local testing...")

    params = {
        "TableName": table,
        "KeySchema": [
            {"AttributeName": "QuotaCode", "KeyType": "HASH"},
            {"AttributeName": "ServiceCode", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "QuotaCode", "AttributeType": "S"},
            {"AttributeName": "ServiceCode", "AttributeType": "S"},
        ],
    }
    if billing_mode == "PAY_PER_REQUEST":
        params["BillingMode"] = "PAY_PER_REQUEST"
    else:
        params["ProvisionedThroughput"] = {
            "ReadCapacityUnits": read_capacity,
            "WriteCapacityUnits": write_capacity,
        }

    table_ref = dynamodb.create_table(**params)
    table_ref.wait_until_exists()
    print(f"DynamoDB table '{table}' is ready")


def load_lambda_module():
    """Load src/qm-quotalist/main.py as a module so we can call lambda_handler locally."""
    if not LAMBDA_SOURCE.exists():
        raise FileNotFoundError(f"Cannot find Lambda source at {LAMBDA_SOURCE}")

    spec = importlib.util.spec_from_file_location("qm_quotalist_lambda", LAMBDA_SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


if __name__ == "__main__":
    main()
