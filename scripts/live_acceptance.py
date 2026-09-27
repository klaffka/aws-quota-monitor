"""Opt-in synchronous acceptance under the deployed Lambda execution role.

Writes monitor records and incurs a normal collection's API costs. Does not
create application fixtures or send quota notifications. Never called by CI.
"""
import argparse
from datetime import datetime, UTC
import json
from uuid import uuid4

import boto3
from botocore.config import Config


def acceptance(session, function, qualifier, table, expected_account, required_services=()):
    account = session.client('sts').get_caller_identity()['Account']
    if account != expected_account:
        raise ValueError('AWS account does not match --expected-account')
    event = {'source': 'manual-validation', 'time': datetime.now(UTC).isoformat(),
             'runId': f'acceptance-{uuid4().hex}', 'validation': True}
    client = session.client('lambda', config=Config(read_timeout=960, retries={'total_max_attempts': 1}))
    response = client.invoke(FunctionName=function, Qualifier=qualifier,
                             InvocationType='RequestResponse', Payload=json.dumps(event).encode())
    payload = json.loads(response['Payload'].read())
    if response.get('FunctionError') or payload.get('statusCode') != 200:
        raise RuntimeError('Collector acceptance failed; inspect Lambda logs and RUN# errors')
    result = json.loads(payload['body'])
    if not result.get('runId') or result.get('duplicate') or result.get('measurements', 0) <= 0:
        raise RuntimeError('Collector returned no fresh, identified measurements')
    from boto3.dynamodb.conditions import Key
    resource = session.resource('dynamodb').Table(table)
    from modules.qmcore.model import iso
    end = datetime.fromisoformat(event['time'])
    run = resource.get_item(Key={'PK': f'RUN#{account}#{session.region_name}',
                                 'SK': f'TS#{iso(end)}'}, ConsistentRead=True).get('Item', {})
    if run.get('runId') != result['runId'] or run.get('qualityStatus') != 'OK' or run.get('alertsEnabled') is not False:
        raise RuntimeError('Run record does not confirm a successful notification-free acceptance')
    # Optional populated-service assertions distinguish inventory correctness
    # from an empty-account smoke test. Query each known service's quota keys.
    from modules.qmcore.registry import custom_keys
    for service in required_services:
        populated = False
        for code in sorted(code for svc, code in custom_keys() if svc == service):
            items = resource.query(KeyConditionExpression=Key('PK').eq(f'QUOTA#{account}#{session.region_name}#quota#{code}')
                                   & Key('SK').eq(f'TS#{iso(end)}'), ConsistentRead=True).get('Items', [])
            populated |= any(item.get('qualityStatus') == 'OK' and item.get('usageValue', 0) > 0 for item in items)
        if not populated:
            raise RuntimeError(f'No positive, valid inventory for required service {service}')
    return {'runId': result['runId'], 'measurements': result['measurements'],
            'executedVersion': response.get('ExecutedVersion'), 'status': 'PASS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-account', required=True)
    parser.add_argument('--region', default='eu-central-1')
    parser.add_argument('--function', default='qm-quota-collector')
    parser.add_argument('--qualifier', default='live')
    parser.add_argument('--table', default='qm-quotalog')
    parser.add_argument('--require-service', action='append', default=[])
    parser.add_argument('--execute', action='store_true', help='Invoke Lambda and write monitor records')
    args = parser.parse_args()
    if not args.execute:
        parser.error('Live writes require --execute; see docs/operations.md')
    print(json.dumps(acceptance(boto3.Session(region_name=args.region), args.function,
                               args.qualifier, args.table, args.expected_account, args.require_service)))


if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    main()
