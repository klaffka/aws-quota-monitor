"""Elastic Load Balancing quota checks from paginated ELBv2 inventories."""
from collections import Counter, defaultdict

from modules.qmcore.aws import CheckContext, maximum, session_from_env


def lbs(ctx):
    return ctx.call("elbv2", "describe_load_balancers", "LoadBalancers")


def classic_lbs(ctx):
    return ctx.call("elb", "describe_load_balancers", "LoadBalancerDescriptions")


def target_groups(ctx):
    return ctx.call("elbv2", "describe_target_groups", "TargetGroups")


def listeners(ctx, lb_arn):
    return ctx.call("elbv2", "describe_listeners", "Listeners", LoadBalancerArn=lb_arn)


def rules(ctx, listener_arn):
    return ctx.call("elbv2", "describe_rules", "Rules", ListenerArn=listener_arn)


def targets(ctx, group_arn):
    return ctx.call("elbv2", "describe_target_health", "TargetHealthDescriptions",
                    TargetGroupArn=group_arn)


def certificates_per_lb(ctx, kind):
    values = []
    for lb in lbs(ctx):
        if lb.get("Type") != kind:
            continue
        count = 0
        for listener in listeners(ctx, lb["LoadBalancerArn"]):
            count += len(ctx.call("elbv2", "describe_listener_certificates", "Certificates",
                                  ListenerArn=listener["ListenerArn"]))
        values.append((lb["LoadBalancerArn"], count, None))
    return maximum(values, "LoadBalancer", "elbv2:DescribeListenerCertificates")


def targets_per_az_nlb(ctx):
    values = []
    for lb in lbs(ctx):
        if lb.get("Type") != "network":
            continue
        groups = [g for g in target_groups(ctx) if lb["LoadBalancerArn"] in g.get("LoadBalancerArns", [])]
        counts = Counter()
        for group in groups:
            for description in targets(ctx, group["TargetGroupArn"]):
                target = description.get("Target", {})
                az = target.get("AvailabilityZone")
                if not az:
                    raise ValueError(f"Target {target.get('Id')} has no AvailabilityZone")
                counts[az] += 1
        values.extend((f"{lb['LoadBalancerArn']}:{az}", count, {"loadBalancer": lb["LoadBalancerArn"], "availabilityZone": az})
                      for az, count in counts.items())
    return maximum(values, "AvailabilityZone", "elbv2:DescribeTargetHealth")


def trust_stores(ctx):
    return ctx.call("elbv2", "describe_trust_stores", "TrustStores")


def revocation_entries(ctx):
    return maximum([(store["TrustStoreArn"], store.get("TotalRevokedEntries", 0), None)
                    for store in trust_stores(ctx)], "TrustStore", "elbv2:DescribeTrustStores")


def revocation_lists(ctx):
    values = []
    for store in trust_stores(ctx):
        revocations = ctx.call("elbv2", "describe_trust_store_revocations", "TrustStoreRevocations",
                               TrustStoreArn=store["TrustStoreArn"])
        values.append((store["TrustStoreArn"], len(revocations), None))
    return maximum(values, "TrustStore", "elbv2:DescribeTrustStoreRevocations")


def ca_certificates(ctx):
    return maximum([(store["TrustStoreArn"], store.get("NumberOfCaCertificates", 0), None)
                    for store in trust_stores(ctx)], "TrustStore", "elbv2:DescribeTrustStores")


def capacity_reservations(ctx, kind, regional=False, per_az=False):
    values = []
    for lb in lbs(ctx):
        if lb.get("Type") != kind:
            continue
        reservation = ctx.call("elbv2", "describe_capacity_reservation",
                               LoadBalancerArn=lb["LoadBalancerArn"])
        if regional:
            values.append((lb["LoadBalancerArn"], sum(s.get("EffectiveCapacityUnits", 0)
                                                       for s in reservation.get("CapacityReservationState", [])), None))
        elif per_az:
            values.extend((f"{lb['LoadBalancerArn']}:{state.get('AvailabilityZone')}",
                           state.get("EffectiveCapacityUnits", 0), None)
                          for state in reservation.get("CapacityReservationState", []))
        else:
            values.append((lb["LoadBalancerArn"], reservation.get("MinimumLoadBalancerCapacity", {}).get("CapacityUnits", 0), None))
    if regional:
        return dict(usage=sum(value for _, value, _ in values), source="elbv2:DescribeCapacityReservation",
                    method="REGION_TOTAL")
    return maximum(values, "LoadBalancer" if not per_az else "AvailabilityZone",
                   "elbv2:DescribeCapacityReservation")


def by_type(ctx, kind):
    count = sum(lb.get("Type") == kind for lb in lbs(ctx))
    return dict(usage=count, source="elbv2:DescribeLoadBalancers",
                method="REGION_TOTAL", meta={"type": kind})


def regional_target_groups(ctx):
    return dict(usage=len(target_groups(ctx)), source="elbv2:DescribeTargetGroups",
                method="REGION_TOTAL")


def target_groups_per_lb(ctx):
    counts = defaultdict(int)
    for group in target_groups(ctx):
        for arn in group.get("LoadBalancerArns", []):
            counts[arn] += 1
    return maximum([(arn, count, None) for arn, count in counts.items()],
                   "LoadBalancer", "elbv2:DescribeTargetGroups")


def listeners_per_lb(ctx, kind=None):
    values = []
    for lb in lbs(ctx):
        if kind and lb.get("Type") != kind:
            continue
        values.append((lb["LoadBalancerArn"], len(listeners(ctx, lb["LoadBalancerArn"])), None))
    return maximum(values, "LoadBalancer", "elbv2:DescribeLoadBalancers+DescribeListeners")


def rules_per_alb(ctx):
    values = []
    for lb in lbs(ctx):
        if lb.get("Type") != "application":
            continue
        count = sum(len(rules(ctx, listener["ListenerArn"]))
                    for listener in listeners(ctx, lb["LoadBalancerArn"]))
        values.append((lb["LoadBalancerArn"], count, None))
    return maximum(values, "ApplicationLoadBalancer", "elbv2:DescribeRules")


def targets_per_group(ctx):
    values = []
    for group in target_groups(ctx):
        values.append((group["TargetGroupArn"], len(targets(ctx, group["TargetGroupArn"])), None))
    return maximum(values, "TargetGroup", "elbv2:DescribeTargetHealth")


def targets_per_lb(ctx, kind):
    groups = defaultdict(set)
    for group in target_groups(ctx):
        for lb in group.get("LoadBalancerArns", []):
            groups[lb].update(d.get("Target", {}).get("Id") for d in targets(ctx, group["TargetGroupArn"]))
    values = [(lb, len({target for target in ids if target}), {"type": kind})
              for lb, ids in groups.items()
              if any(item["LoadBalancerArn"] == lb and item.get("Type") == kind for item in lbs(ctx))]
    return maximum(values, "LoadBalancer", "elbv2:DescribeTargetHealth")


CHECKS = [
    ("L-E9E9831D", "Classic Load Balancers per Region", lambda c: dict(usage=len(classic_lbs(c)), source="elb:DescribeLoadBalancers", method="REGION_TOTAL")),
    ("L-53DA6B97", "Application Load Balancers per Region", lambda c: by_type(c, "application")),
    ("L-69A177A2", "Network Load Balancers per Region", lambda c: by_type(c, "network")),
    ("L-B22855CB", "Target Groups per Region", regional_target_groups),
    ("L-822D1B1B", "Target Groups per Application Load Balancer", target_groups_per_lb),
    ("L-B6DF7632", "Listeners per Application Load Balancer", lambda c: listeners_per_lb(c, "application")),
    ("L-57A373D6", "Listeners per Network Load Balancer", lambda c: listeners_per_lb(c, "network")),
    ("L-7EED9B64", "Rules per Application Load Balancer", rules_per_alb),
    ("L-A0D0B863", "Targets per Target Group per Region", targets_per_group),
    ("L-7E6692B2", "Targets per Application Load Balancer", lambda c: targets_per_lb(c, "application")),
    ("L-EEF1AD04", "Targets per Network Load Balancer", lambda c: targets_per_lb(c, "network")),
    ("L-9365A611", "Certificates per Application Load Balancer", lambda c: certificates_per_lb(c, "application")),
    ("L-52964454", "Certificates per Network Load Balancer", lambda c: certificates_per_lb(c, "network")),
    ("L-B211E961", "Targets per Availability Zone per Network Load Balancer", targets_per_az_nlb),
    ("L-37E1617B", "Revocation entries per trust store", revocation_entries),
    ("L-332EE142", "Revocation lists per trust store", revocation_lists),
    ("L-A8F7060B", "Trust stores per account", lambda c: dict(usage=len(trust_stores(c)), source="elbv2:DescribeTrustStores", method="REGION_TOTAL")),
    ("L-43FE5A42", "CA certificates per trust store", ca_certificates),
    ("L-0BB7B635", "Reserved Application Load Balancer Capacity Units per Application Load Balancer", lambda c: capacity_reservations(c, "application")),
    ("L-723DCCB6", "Reserved Network Load Balancer Capacity Units per Region", lambda c: capacity_reservations(c, "network", regional=True)),
    ("L-7C45F98A", "Reserved Network Load Balancer Capacity Units per Network Load Balancer, per availability zone", lambda c: capacity_reservations(c, "network", per_az=True)),
    ("L-7A15E3C5", "Reserved Gateway Load Balancer Capacity Units per Region", lambda c: capacity_reservations(c, "gateway", regional=True)),
    ("L-9E6F9012", "Reserved Gateway Load Balancer Capacity Units per Gateway Load Balancer, per availability zone", lambda c: capacity_reservations(c, "gateway", per_az=True)),
]


def get_current_quotastatus_elb(session=None, *, ctx=None, skip=()):
    return (ctx or CheckContext(session or session_from_env())).run("elasticloadbalancing", CHECKS, skip)
