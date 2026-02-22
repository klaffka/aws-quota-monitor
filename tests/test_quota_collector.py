#!/usr/bin/env python3
"""
Test script for quota-collector Lambda function
Invokes the function and retrieves logs
"""

import boto3
import json
import sys
import os
import time
from datetime import datetime, timedelta

# Get AWS profile from environment or use default
PROFILE = os.environ.get('AWS_PROFILE', 'BA')
REGION = os.environ.get('AWS_REGION', 'eu-central-1')
FUNCTION_NAME = 'qm-quota-collector'


def invoke_lambda(session):
    """Invoke the quota-collector Lambda function"""
    lambda_client = session.client('lambda', region_name=REGION)
    
    print(f"Invoking {FUNCTION_NAME}...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        # Parse the response
        payload = json.loads(response['Payload'].read())
        
        print(f"\n{'='*60}")
        print(f"Lambda Response Status: {response['StatusCode']}")
        print(f"{'='*60}")
        print(json.dumps(payload, indent=2))
        
        # Get logs
        get_logs(session)
        
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
                limit=50
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
