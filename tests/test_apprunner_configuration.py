
import pytest

from modules.qmchecks.apprunner import (
    auto_scaling_configuration_count,
    connection_count,
    observability_configuration_count,
    vpc_connector_count,
    vpc_ingress_connections_per_service,
)
from modules.qmcore.aws import NoData
from tests.iam_policy import grants


class AppRunnerContext:
    inventories = {
        'list_connections': [
            {'ConnectionArn': 'arn:connection:one', 'Status': 'AVAILABLE'},
            {'ConnectionArn': 'arn:connection:deleted', 'Status': 'DELETED'},
        ],
        'list_auto_scaling_configurations': [
            {'AutoScalingConfigurationName': 'scaling-one', 'Status': 'active'},
            {'AutoScalingConfigurationName': 'scaling-old', 'Status': 'INACTIVE'},
        ],
        'list_observability_configurations': [
            {'ObservabilityConfigurationName': 'tracing-one'},
            {'ObservabilityConfigurationName': 'tracing-two'},
        ],
        'list_vpc_connectors': [
            {'VpcConnectorName': 'connector-one', 'Status': 'ACTIVE'},
            {'VpcConnectorName': 'connector-old', 'Status': 'INACTIVE'},
        ],
        'list_vpc_ingress_connections': [
            {'VpcIngressConnectionArn': 'arn:ingress:one',
             'ServiceArn': 'arn:service:a'},
            {'VpcIngressConnectionArn': 'arn:ingress:two',
             'ServiceArn': 'arn:service:a'},
            {'VpcIngressConnectionArn': 'arn:ingress:three',
             'ServiceArn': 'arn:service:b'},
        ],
    }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'apprunner'
        if method in {'list_auto_scaling_configurations',
                      'list_observability_configurations'}:
            assert kwargs == {'LatestOnly': True}
        else:
            assert kwargs == {}
        return self.inventories[method]


def test_apprunner_account_configuration_counts_use_latest_active_names():
    ctx = AppRunnerContext()
    assert connection_count(ctx)['usage'] == 1
    assert auto_scaling_configuration_count(ctx)['usage'] == 1
    assert observability_configuration_count(ctx)['usage'] == 2
    assert vpc_connector_count(ctx)['usage'] == 1


def test_apprunner_vpc_ingress_is_maximum_per_service():
    result = vpc_ingress_connections_per_service(AppRunnerContext())
    assert (result['usage'], result['resource_id']) == (2, 'arn:service:a')
    assert result['meta'] is None


def test_apprunner_configuration_rejects_duplicates_and_unknown_states():
    ctx = AppRunnerContext()
    ctx.inventories = {**ctx.inventories, 'list_connections': [
        {'ConnectionArn': 'arn:connection:one', 'Status': 'AVAILABLE'},
        {'ConnectionArn': 'arn:connection:one', 'Status': 'ERROR'},
    ]}
    with pytest.raises(NoData, match='duplicate identity'):
        connection_count(ctx)

    ctx = AppRunnerContext()
    ctx.inventories = {**ctx.inventories, 'list_vpc_connectors': [
        {'VpcConnectorName': 'connector-one', 'Status': 'CREATING'},
    ]}
    with pytest.raises(NoData, match='unknown status'):
        vpc_connector_count(ctx)


def test_apprunner_configuration_checks_have_read_permissions():
    for action in (
        'ListConnections', 'ListAutoScalingConfigurations',
        'ListVpcIngressConnections', 'ListObservabilityConfigurations',
        'ListVpcConnectors',
    ):
        assert grants(f'apprunner:{action}')
