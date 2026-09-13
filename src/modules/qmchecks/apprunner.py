"""AWS App Runner regional resource inventories."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def _unique_count(ctx, method, key, identity_field, *, kwargs=None,
                  status_field=None, counted_statuses=None, ignored_statuses=None):
    identities = set()
    for item in ctx.call('apprunner', method, key, **(kwargs or {})):
        if not isinstance(item, dict):
            raise NoData(f'App Runner {key} inventory contains an invalid item')
        identity = item.get(identity_field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'App Runner {key} inventory item is missing {identity_field}')
        if status_field:
            status = item.get(status_field)
            if not isinstance(status, str):
                raise NoData(f'App Runner {key} inventory contains an unknown status')
            status = status.upper()
            if status in (ignored_statuses or set()):
                continue
            if status not in (counted_statuses or set()):
                raise NoData(f'App Runner {key} inventory contains an unknown status')
        if identity in identities:
            raise NoData(f'App Runner {key} inventory contains a duplicate identity')
        identities.add(identity)
    return dict(usage=len(identities), source=f'apprunner:{method}',
                method='ACCOUNT_COUNT')


def connection_count(ctx):
    return _unique_count(
        ctx, 'list_connections', 'ConnectionSummaryList', 'ConnectionArn',
        status_field='Status',
        counted_statuses={'PENDING_HANDSHAKE', 'AVAILABLE', 'ERROR'},
        ignored_statuses={'DELETED'})


def auto_scaling_configuration_count(ctx):
    return _unique_count(
        ctx, 'list_auto_scaling_configurations',
        'AutoScalingConfigurationSummaryList', 'AutoScalingConfigurationName',
        kwargs={'LatestOnly': True}, status_field='Status',
        counted_statuses={'ACTIVE'}, ignored_statuses={'INACTIVE'})


def observability_configuration_count(ctx):
    return _unique_count(
        ctx, 'list_observability_configurations',
        'ObservabilityConfigurationSummaryList', 'ObservabilityConfigurationName',
        kwargs={'LatestOnly': True})


def vpc_connector_count(ctx):
    return _unique_count(
        ctx, 'list_vpc_connectors', 'VpcConnectors', 'VpcConnectorName',
        status_field='Status', counted_statuses={'ACTIVE'},
        ignored_statuses={'INACTIVE'})


def vpc_ingress_connections_per_service(ctx):
    counts = Counter()
    identities = set()
    for item in ctx.call('apprunner', 'list_vpc_ingress_connections',
                         'VpcIngressConnectionSummaryList'):
        if not isinstance(item, dict):
            raise NoData('App Runner VPC ingress inventory contains an invalid item')
        arn = item.get('VpcIngressConnectionArn')
        service_arn = item.get('ServiceArn')
        if (not isinstance(arn, str) or not arn
                or not isinstance(service_arn, str) or not service_arn):
            raise NoData('App Runner VPC ingress connection is missing an identity')
        if arn in identities:
            raise NoData('App Runner VPC ingress inventory contains a duplicate identity')
        identities.add(arn)
        counts[service_arn] += 1
    return maximum(((service_arn, count, None)
                    for service_arn, count in counts.items()),
                   'AppRunnerService', 'apprunner:ListVpcIngressConnections')


CHECKS = [
    ('L-69F96A0C', 'Services',
     lambda ctx: dict(usage=len(ctx.call('apprunner', 'list_services',
                                        'ServiceSummaryList')),
                      source='apprunner:ListServices', method='ACCOUNT_COUNT')),
    ('L-1BDBAAB6', 'Connections', connection_count),
    ('L-1D8C5BDD', 'Auto scaling configurations',
     auto_scaling_configuration_count),
    ('L-4064914D', 'VPC ingress connections',
     vpc_ingress_connections_per_service),
    ('L-A0B46A0C', 'Observability configurations',
     observability_configuration_count),
    ('L-F7ADEB8C', 'VPC connectors', vpc_connector_count),
]


def get_current_quotastatus_apprunner(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'apprunner' for service, _ in context.quotas): return []
    return context.run('apprunner', CHECKS, skip)
