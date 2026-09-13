#!/usr/bin/env python3
"""Export the official AWS utilization report; preserve its ID for safe resumption."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import boto3
from modules.qmcore.aws import CONFIG
from modules.qmcore.utilization import ReportPending, read_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile')
    parser.add_argument('--region', default='eu-central-1')
    parser.add_argument('--report-id', help='Resume an existing AWS report instead of starting another')
    parser.add_argument('--output', required=True)
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    client = boto3.Session(profile_name=args.profile, region_name=args.region).client('service-quotas', config=CONFIG)
    destination = Path(args.output)
    state = destination.with_suffix(destination.suffix + '.state.json')
    report_id = args.report_id
    if not report_id:
        if state.exists():
            parser.error(f'Existing report state at {state}; resume using its ReportId with --report-id')
        response = client.start_quota_utilization_report()
        report_id = response['ReportId']
        state.write_text(json.dumps({'ReportId': report_id, 'Region': args.region, 'Profile': args.profile}, indent=2))
        print(f'Started report {report_id}; resume state: {state}', flush=True)
    deadline = time.monotonic() + args.timeout
    while True:
        try:
            report = read_report(client, report_id)
        except ReportPending as exc:
            if time.monotonic() >= deadline:
                print(f'{exc}; resume with --report-id {report_id}', file=sys.stderr)
                return 2
            print(str(exc), flush=True)
            time.sleep(min(5, max(0, deadline - time.monotonic())))
            continue
        report['Region'] = args.region
        destination.write_text(json.dumps(report, indent=2, default=lambda value: value.isoformat()))
        print(f"Saved complete report with {report['TotalCount']} quotas to {destination}", flush=True)
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
