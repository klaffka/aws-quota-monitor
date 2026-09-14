from unittest.mock import Mock

from modules.qmchecks.elb import (
    by_type, target_groups_per_lb, listeners_per_lb, rules_per_alb,
    targets_per_group, targets_per_lb, ca_certificates, capacity_reservations,
)


def context():
    ctx = Mock()
    ctx.call = Mock()
    return ctx


def test_load_balancers_are_counted_by_type():
    ctx = context()
    ctx.call.return_value = [
        {"LoadBalancerArn": "arn:alb", "Type": "application"},
        {"LoadBalancerArn": "arn:nlb", "Type": "network"},
        {"LoadBalancerArn": "arn:alb2", "Type": "application"},
    ]
    assert by_type(ctx, "application")["usage"] == 2


def test_target_groups_per_alb_and_target_group_maxima():
    ctx = context()
    groups = [
        {"TargetGroupArn": "tg-1", "LoadBalancerArns": ["alb-1"]},
        {"TargetGroupArn": "tg-2", "LoadBalancerArns": ["alb-1"]},
        {"TargetGroupArn": "tg-3", "LoadBalancerArns": ["alb-2"]},
    ]
    ctx.call.return_value = groups
    assert target_groups_per_lb(ctx)["usage"] == 2

    def calls(service, method, key=None, **kwargs):
        if method == "describe_target_groups":
            return groups
        if method == "describe_target_health":
            return [{"Target": {"Id": f"i-{n}"}} for n in range(3 if kwargs["TargetGroupArn"] == "tg-1" else 1)]
        return []
    ctx.call.side_effect = calls
    result = targets_per_group(ctx)
    assert result["usage"] == 3 and result["resource_id"] == "tg-1"


def test_listeners_and_rules_are_scoped_to_application_load_balancers():
    ctx = context()
    def calls(service, method, key=None, **kwargs):
        if method == "describe_load_balancers":
            return [{"LoadBalancerArn": "alb-1", "Type": "application"},
                    {"LoadBalancerArn": "nlb-1", "Type": "network"}]
        if method == "describe_listeners":
            return [{"ListenerArn": "listener-1"}] if kwargs["LoadBalancerArn"] == "alb-1" else [{"ListenerArn": "listener-2"}]
        if method == "describe_rules":
            return [{"RuleArn": f"rule-{i}"} for i in range(4)]
        return []
    ctx.call.side_effect = calls
    assert listeners_per_lb(ctx, "application")["usage"] == 1
    assert rules_per_alb(ctx)["usage"] == 4


def test_targets_per_load_balancer_deduplicates_targets_across_groups():
    ctx = context()
    def calls(service, method, key=None, **kwargs):
        if method == "describe_load_balancers":
            return [{"LoadBalancerArn": "alb-1", "Type": "application"}]
        if method == "describe_target_groups":
            return [{"TargetGroupArn": "tg-1", "LoadBalancerArns": ["alb-1"]},
                    {"TargetGroupArn": "tg-2", "LoadBalancerArns": ["alb-1"]}]
        if method == "describe_target_health":
            return [{"Target": {"Id": "i-1"}}, {"Target": {"Id": "i-2"}}] if kwargs["TargetGroupArn"] == "tg-1" else [{"Target": {"Id": "i-2"}}]
        return []
    ctx.call.side_effect = calls
    result = targets_per_lb(ctx, "application")
    assert result["usage"] == 2


def test_trust_store_ca_certificates_and_capacity_reservations():
    ctx = context()
    def calls(service, method, key=None, **kwargs):
        if method == "describe_trust_stores":
            return [{"TrustStoreArn": "ts-1", "NumberOfCaCertificates": 4}]
        if method == "describe_load_balancers":
            return [{"LoadBalancerArn": "alb-1", "Type": "application"}]
        if method == "describe_capacity_reservation":
            return {"MinimumLoadBalancerCapacity": {"CapacityUnits": 12}, "CapacityReservationState": []}
        return []
    ctx.call.side_effect = calls
    assert ca_certificates(ctx)["usage"] == 4
    assert capacity_reservations(ctx, "application")["usage"] == 12


def test_gateway_capacity_reservations_use_same_api():
    ctx = context()
    def calls(service, method, key=None, **kwargs):
        if method == "describe_load_balancers":
            return [{"LoadBalancerArn": "gwlb-1", "Type": "gateway"}]
        if method == "describe_capacity_reservation":
            return {"CapacityReservationState": [
                {"AvailabilityZone": "az-1", "EffectiveCapacityUnits": 5},
                {"AvailabilityZone": "az-2", "EffectiveCapacityUnits": 7},
            ]}
        return []
    ctx.call.side_effect = calls
    assert capacity_reservations(ctx, "gateway", regional=True)["usage"] == 12
