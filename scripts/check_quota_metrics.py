#!/usr/bin/env python3
"""Check specific quotas for UsageMetric availability."""
import boto3

session = boto3.Session()
sq = session.client("service-quotas")

codes = {
    "vpc": ["L-BB24F6E5", "L-CD17FD4B", "L-F678F1CE", "L-E79EC296",
            "L-DF5E4CA3", "L-A4707A72", "L-29B6F2EB", "L-0EA8095F",
            "L-2AEEBF1A", "L-2AFB9258", "L-83CA0A9D", "L-085A6257",
            "L-B4A6D682", "L-589F43AA", "L-407747CB", "L-7E9ECCDB",
            "L-12E49864", "L-FE5A380F", "L-5F53652F", "L-DFA99DE7",
            "L-DC9F7029", "L-1B52E74A", "L-45FE3B85", "L-93826ACB",
            "L-CA6CC422", "L-3B4E38D2", "L-A272D574", "L-42B9C2CA",
            "L-2C462E13", "L-44499CD2"],
    "lambda": ["L-B99A9384", "L-2ACBD22F", "L-75F48B05", "L-01237738",
               "L-6581F036", "L-07A00131", "L-C952DDE4"],
    "ec2": ["L-70015FFA", "L-9A1BC94B", "L-8EA77D34", "L-2C8F52B3",
            "L-CFF3E941"]
}

for svc, qcodes in codes.items():
    print(f"\n=== {svc.upper()} ===")
    for qc in qcodes:
        try:
            resp = sq.get_service_quota(ServiceCode=svc, QuotaCode=qc)
            q = resp["Quota"]
            um = q.get("UsageMetric")
            name = q.get("QuotaName", "?")[:55]
            if um:
                ns = um.get("MetricNamespace", "")
                mn = um.get("MetricName", "")
                dims = um.get("MetricDimensions", {})
                marker = "*** NON-AWS/Usage ***" if ns != "AWS/Usage" else "AWS/Usage"
                print(f"  {qc}  {name:<55}  {marker}  NS={ns}  M={mn}")
                if dims:
                    print(f"         dims={dims}")
            else:
                print(f"  {qc}  {name:<55}  NO METRIC")
        except Exception as e:
            print(f"  {qc}  ERROR: {e}")
