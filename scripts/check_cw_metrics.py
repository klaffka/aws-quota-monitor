#!/usr/bin/env python3
"""Check CloudWatch for non-AWS/Usage metrics relevant to quota monitoring."""
import boto3

session = boto3.Session()
cw = session.client('cloudwatch')

# 1) Search for NAU metrics across namespaces
print("=== Searching for NAU metrics ===")
for ns in ["AWS/EC2", "AWS/VPC", "AWS/Usage", "AWS/NATGateway"]:
    for mn in ["NetworkAddressUsage", "PeeredNetworkAddressUsage",
               "NetworkAddressUsagePerVpc"]:
        resp = cw.list_metrics(Namespace=ns, MetricName=mn)
        metrics = resp.get("Metrics", [])
        if metrics:
            print(f"  {ns} / {mn}: {len(metrics)} metrics")
            for m in metrics[:3]:
                print(f"    dims={m.get('Dimensions')}")

# 2) Check AWS/Lambda namespace for all metrics (non-AWS/Usage)
print("\n=== AWS/Lambda namespace metrics ===")
resp = cw.list_metrics(Namespace="AWS/Lambda")
metric_names = set()
for m in resp.get("Metrics", []):
    metric_names.add(m["MetricName"])
for mn in sorted(metric_names):
    print(f"  {mn}")

# 3) Check AWS/NATGateway namespace
print("\n=== AWS/NATGateway namespace metrics ===")
resp = cw.list_metrics(Namespace="AWS/NATGateway")
metric_names = set()
for m in resp.get("Metrics", []):
    metric_names.add(m["MetricName"])
for mn in sorted(metric_names):
    print(f"  {mn}")

# 4) Check AWS/EC2 for any non-instance metrics
print("\n=== AWS/EC2 namespace metric names (unique) ===")
resp = cw.list_metrics(Namespace="AWS/EC2")
metric_names = set()
for m in resp.get("Metrics", []):
    metric_names.add(m["MetricName"])
for mn in sorted(metric_names):
    print(f"  {mn}")

# 5) AWS/VPC namespace
print("\n=== AWS/VPC namespace ===")
resp = cw.list_metrics(Namespace="AWS/VPC")
metric_names = set()
for m in resp.get("Metrics", []):
    metric_names.add(m["MetricName"])
if metric_names:
    for mn in sorted(metric_names):
        print(f"  {mn}")
else:
    print("  (no metrics found)")

# 6) Check for VPC-related metrics in AWS/Usage
print("\n=== AWS/Usage VPC-related ResourceCount ===")
paginator = cw.get_paginator("list_metrics")
for page in paginator.paginate(Namespace="AWS/Usage", MetricName="ResourceCount"):
    for m in page.get("Metrics", []):
        dims = {d["Name"]: d["Value"] for d in m.get("Dimensions", [])}
        svc = dims.get("Service", "")
        if svc == "EC2":
            res = dims.get("Resource", "")
            # Show VPC-related resources
            keywords = ["VPC", "Subnet", "Security", "NAT", "Network",
                        "Route", "Endpoint", "Peering", "Gateway", "ACL",
                        "Interface"]
            if any(kw in res for kw in keywords):
                print(f"  Resource={res}  Class={dims.get('Class', '')}  Type={dims.get('Type', '')}")
