from pathlib import Path

import pytest

from modules.qmchecks.application_autoscaling import (
    SERVICE_NAMESPACES,
    scaling_policies_per_target,
    scheduled_actions_per_target,
    step_adjustments_per_policy,
)
from modules.qmcore.aws import NoData


class ScalingContext:
    def __init__(self):
        self.calls = []
        self.actions = [
            {'ScheduledActionARN': 'arn:action:one', 'ServiceNamespace': 'ecs',
             'ResourceId': 'service/cluster/one',
             'ScalableDimension': 'ecs:service:DesiredCount'},
            {'ScheduledActionARN': 'arn:action:two', 'ServiceNamespace': 'ecs',
             'ResourceId': 'service/cluster/one',
             'ScalableDimension': 'ecs:service:DesiredCount'},
            {'ScheduledActionARN': 'arn:action:three', 'ServiceNamespace': 'ecs',
             'ResourceId': 'service/cluster/two',
             'ScalableDimension': 'ecs:service:DesiredCount'},
        ]
        self.policies = [
            {'PolicyARN': 'arn:policy:one', 'PolicyType': 'StepScaling',
             'ServiceNamespace': 'ecs', 'ResourceId': 'service/cluster/one',
             'ScalableDimension': 'ecs:service:DesiredCount',
             'StepScalingPolicyConfiguration': {
                 'StepAdjustments': [{}, {}, {}],
             }},
            {'PolicyARN': 'arn:policy:two', 'PolicyType': 'TargetTrackingScaling',
             'ServiceNamespace': 'ecs', 'ResourceId': 'service/cluster/one',
             'ScalableDimension': 'ecs:service:DesiredCount'},
            {'PolicyARN': 'arn:policy:three', 'PolicyType': 'PredictiveScaling',
             'ServiceNamespace': 'ecs', 'ResourceId': 'service/cluster/two',
             'ScalableDimension': 'ecs:service:DesiredCount'},
        ]

    def call(self, service, method, key=None, **kwargs):
        assert service == 'application-autoscaling'
        namespace = kwargs['ServiceNamespace']
        self.calls.append((method, namespace))
        if namespace != 'ecs':
            return []
        if method == 'describe_scheduled_actions':
            assert key == 'ScheduledActions'
            return self.actions
        if method == 'describe_scaling_policies':
            assert key == 'ScalingPolicies'
            return self.policies
        raise AssertionError(method)


def test_scheduled_actions_use_maximum_per_scalable_target_across_namespaces():
    ctx = ScalingContext()
    result = scheduled_actions_per_target(ctx)
    assert result['usage'] == 2
    assert result['resource_id'].endswith('service/cluster/one/ecs:service:DesiredCount')
    assert {namespace for _, namespace in ctx.calls} == set(SERVICE_NAMESPACES)


def test_scaling_policy_and_step_adjustment_scopes_are_distinct():
    ctx = ScalingContext()
    result = scaling_policies_per_target(ctx)
    assert result['usage'] == 2
    assert result['resource_id'].endswith('service/cluster/one/ecs:service:DesiredCount')

    result = step_adjustments_per_policy(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'arn:policy:one')
    assert result['meta'] is None


def test_application_autoscaling_rejects_duplicate_and_malformed_policies():
    ctx = ScalingContext()
    ctx.policies.append(dict(ctx.policies[0]))
    with pytest.raises(NoData, match='contains a duplicate'):
        scaling_policies_per_target(ctx)

    ctx = ScalingContext()
    ctx.policies[0]['StepScalingPolicyConfiguration']['StepAdjustments'] = None
    with pytest.raises(NoData, match='invalid adjustments'):
        step_adjustments_per_policy(ctx)


def test_application_autoscaling_configuration_has_read_permissions():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"application-autoscaling:DescribeScheduledActions"' in policy
    assert '"application-autoscaling:DescribeScalingPolicies"' in policy
