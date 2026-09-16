import json
import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.catalog import get_catalog
from modules.qmcore.reporting import report_period, build_report, generate_csv_report
from modules.qmcore.model import iso
from modules.qmdb.db import QuotaLogDb


def lambda_handler(event, context):
    start, end = report_period(event)
    bucket = os.getenv('QM_REPORT_BUCKET')
    if not bucket:
        raise ValueError('QM_REPORT_BUCKET must be configured')
    session = session_from_env()
    ctx, db = CheckContext(session), QuotaLogDb(session)
    errors = []
    try:
        quotas, errors = get_catalog(ctx, db, force=True)
    except Exception as exc:
        quotas = []
        errors.append(f'Catalog unavailable: {exc}')
    rows, report_errors = build_report(ctx, db, quotas, start, end)
    errors.extend(report_errors)
    partial = not rows or bool(errors) or any(r['qualityStatus'] in {'NO_DATA', 'ERROR'} for r in rows)
    status = 'PARTIAL' if partial else 'COMPLETE'
    for row in rows:
        row['reportStatus'] = status
    key = f"reports/{ctx.account}/{ctx.region}/{start:%Y-%m-%d}_{end:%Y-%m-%d}/quota-report-{uuid4().hex}.csv"
    ctx.client('s3').put_object(Bucket=bucket, Key=key, Body=generate_csv_report(rows).encode('utf-8'),
                                ContentType='text/csv; charset=utf-8', Metadata={'report-status': status})
    # A sidecar captures catalog/scan errors even when no quota rows can be generated.
    ctx.client('s3').put_object(Bucket=bucket, Key=key + '.json', ContentType='application/json',
        Body=json.dumps(dict(status=status, errors=errors, account=ctx.account, region=ctx.region,
                             periodStart=iso(start), periodEndExclusive=iso(end), quotas=len(rows))).encode('utf-8'))
    if errors:
        raise RuntimeError(f'Partial report saved to s3://{bucket}/{key}: {len(errors)} operational errors')
    return {'statusCode': 200, 'body': json.dumps({'message': 'Report generated', 'report_status': status,
                                                  's3_location': f's3://{bucket}/{key}', 'quotas_count': len(rows)})}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    event = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(lambda_handler(event, None), indent=2))
