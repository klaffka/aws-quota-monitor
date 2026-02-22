#!/usr/bin/env python3
"""
Test script for reporting Lambda function
Invokes the function, retrieves logs, and downloads the generated CSV from S3
"""

import boto3
import json
import sys
import os
import time
from datetime import datetime, timedelta
import tempfile

# Get AWS profile from environment or use default
PROFILE = os.environ.get('AWS_PROFILE', 'BA')
REGION = os.environ.get('AWS_REGION', 'eu-central-1')
FUNCTION_NAME = 'qm-reporting'
REPORT_BUCKET = os.environ.get('QM_REPORT_BUCKET')
INVOKE_ASYNC = os.environ.get('QM_REPORT_ASYNC', '1') == '1'
POLL_TIMEOUT_SEC = int(os.environ.get('QM_REPORT_POLL_TIMEOUT', '1200'))


def invoke_lambda(session):
    """Invoke the reporting Lambda function"""
    # Increase timeouts for long-running Lambda
    import botocore.config
    config = botocore.config.Config(
        connect_timeout=5,
        read_timeout=1000,  # allow up to ~15 minutes for sync runs
        retries={'max_attempts': 1}
    )
    lambda_client = session.client('lambda', region_name=REGION, config=config)
    
    invocation_type = 'Event' if INVOKE_ASYNC else 'RequestResponse'
    print(f"Invoking {FUNCTION_NAME} ({'async' if INVOKE_ASYNC else 'sync'})...")
    
    event_payload = {
        "days_back": 30
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType=invocation_type,
            Payload=json.dumps(event_payload)
        )
        
        print(f"\n{'='*60}")
        print(f"Lambda Response Status: {response['StatusCode']}")
        print(f"{'='*60}")

        if INVOKE_ASYNC:
            # Async invocation: poll S3 for the latest report
            if not REPORT_BUCKET:
                print("QM_REPORT_BUCKET not set; cannot poll S3 for report.")
                return False
            s3_location = wait_for_latest_report(session, REPORT_BUCKET, POLL_TIMEOUT_SEC)
            if s3_location:
                download_csv_from_s3(session, s3_location)
                return True
            return False

        # Sync invocation: Parse the response payload
        payload = json.loads(response['Payload'].read())
        print(json.dumps(payload, indent=2))

        # Get logs
        get_logs(session)

        # Download CSV if successful
        if response['StatusCode'] == 200 and 's3_location' in payload.get('body', ''):
            try:
                body = json.loads(payload.get('body', '{}'))
                s3_location = body.get('s3_location')
                if s3_location:
                    download_csv_from_s3(session, s3_location)
            except Exception:
                pass

        return response['StatusCode'] == 200
        
    except Exception as e:
        print(f"Error invoking Lambda: {e}")
        return False


def get_logs(session):
    """Retrieve CloudWatch logs for the Lambda function"""
    logs_client = session.client('logs', region_name=REGION)
    
    log_group = f'/aws/lambda/{FUNCTION_NAME}'
    
    try:
        # Get log streams (most recent first)
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not streams_response['logStreams']:
            print(f"\nNo log streams found for {log_group}")
            return
        
        print(f"\n{'='*60}")
        print("CloudWatch Logs:")
        print(f"{'='*60}")
        
        # Get events from the most recent stream
        for stream in streams_response['logStreams']:
            stream_name = stream['logStreamName']
            print(f"\nLog Stream: {stream_name}")
            print(f"Last Event Time: {datetime.fromtimestamp(stream['lastEventTimestamp']/1000)}")
            print("-" * 60)
            
            events_response = logs_client.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                limit=100
            )
            
            for event in events_response['events']:
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                print(f"[{timestamp}] {event['message']}", end='')
            
            # Only show most recent stream
            break
            
    except logs_client.exceptions.ResourceNotFoundException:
        print(f"\nLog group not found: {log_group}")
    except Exception as e:
        print(f"Error retrieving logs: {e}")


def download_csv_from_s3(session, s3_location):
    """Download and display CSV from S3"""
    try:
        # Parse s3://bucket/key format
        if not s3_location.startswith('s3://'):
            print(f"\nInvalid S3 location: {s3_location}")
            return
        
        parts = s3_location.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        
        s3_client = session.client('s3', region_name=REGION)
        
        print(f"\n{'='*60}")
        print("Downloading CSV from S3:")
        print(f"{'='*60}")
        print(f"S3 Location: {s3_location}")
        print("-" * 60)
        
        # Download to temporary file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Display CSV content
        print(csv_content)
        
        # Also save to local file
        local_filename = f"quota-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(local_filename, 'w') as f:
            f.write(csv_content)
        
        print(f"\n✓ CSV saved locally to: {local_filename}")
        
    except Exception as e:
        print(f"\nError downloading CSV from S3: {e}")


def wait_for_latest_report(session, bucket, timeout_sec=1200, prefix='reports/'):
    """Poll S3 for the newest report object and return its s3:// location."""
    s3_client = session.client('s3', region_name=REGION)
    start = time.time()
    latest_key = None

    print(f"\nWaiting up to {timeout_sec}s for report in s3://{bucket}/{prefix}...")
    while time.time() - start < timeout_sec:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get('Contents', [])
        if contents:
            latest = max(contents, key=lambda o: o['LastModified'])
            if latest_key != latest['Key']:
                latest_key = latest['Key']
                s3_location = f"s3://{bucket}/{latest_key}"
                print(f"Found latest report: {s3_location}")
                return s3_location
        time.sleep(10)

    print("Timed out waiting for report in S3.")
    return None


def main():
    """Main entry point"""
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
        
        print(f"AWS Profile: {PROFILE}")
        print(f"Region: {REGION}")
        print(f"Function: {FUNCTION_NAME}")
        print()
        
        # Verify credentials
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"Account: {identity['Account']}")
        print(f"User: {identity['Arn']}")
        print()
        
        # Invoke Lambda
        success = invoke_lambda(session)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
