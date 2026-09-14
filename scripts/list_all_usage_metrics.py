#!/usr/bin/env python3
"""List all quotas for vpc/ec2/lambda with their UsageMetric fields."""
import boto3

session = boto3.Session()
sq = session.client('service-quotas')

for svc in ['vpc', 'ec2', 'lambda']:
    print(f"\n{'='*80}")
    print(f"  SERVICE: {svc}")
    print(f"{'='*80}")

    paginator = sq.get_paginator('list_service_quotas')
    quotas = []
    for page in paginator.paginate(ServiceCode=svc):
        quotas.extend(page.get('Quotas', []))

    with_metric = [q for q in quotas if q.get('UsageMetric')]
    without_metric = [q for q in quotas if not q.get('UsageMetric')]

    print(f"\n  --- WITH UsageMetric ({len(with_metric)}) ---")
    for q in sorted(with_metric, key=lambda x: x['QuotaCode']):
        um = q['UsageMetric']
        ns = um.get('MetricNamespace', '?')
        mn = um.get('MetricName', '?')
        dims = um.get('MetricDimensions', {})
        qname = q['QuotaName']
        print(f"  {q['QuotaCode']}  ns={ns}  metric={mn}")
        print(f"    name={qname}")
        if dims:
            print(f"    dims={dims}")

    print(f"\n  --- WITHOUT UsageMetric ({len(without_metric)}) ---")
    for q in sorted(without_metric, key=lambda x: x['QuotaCode']):
        qname = q['QuotaName']
        print(f"  {q['QuotaCode']}  {qname}")

print("\nDone.")
