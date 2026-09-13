"""Amazon MSK regional resource-count quotas with unambiguous inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def configuration_revisions(ctx):
    values = []
    for configuration in ctx.call('kafka', 'list_configurations', 'Configurations'):
        arn = configuration.get('Arn')
        if arn:
            revisions = ctx.call('kafka', 'list_configuration_revisions', 'Revisions', Arn=arn)
            values.append((arn, len(revisions), None))
    return maximum(values, 'MSKConfiguration',
                   'kafka:ListConfigurations+ListConfigurationRevisions')

CHECKS = [
    ('L-B2FDE22A', 'Number of configurations per account',
     lambda c: dict(usage=len(c.call('kafka', 'list_configurations', 'Configurations')),
                    source='kafka:ListConfigurations', method='ACCOUNT_COUNT')),
    ('L-8F940D28', 'Number of replicators per account',
     lambda c: dict(usage=len(c.call('kafka', 'list_replicators', 'Replicators')),
                    source='kafka:ListReplicators', method='ACCOUNT_COUNT')),
    ('L-EDD31C36', 'Number of brokers per account',
     lambda c: dict(usage=sum((cluster.get('Provisioned') or {}).get('NumberOfBrokerNodes', 0)
                              for cluster in c.call('kafka', 'list_clusters_v2', 'ClusterInfoList')),
                    source='kafka:ListClustersV2', method='ACCOUNT_COUNT')),
    ('L-36D29E8C', 'Number of revisions per configuration', configuration_revisions),
]


def get_current_quotastatus_kafka(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kafka' for service, _ in context.quotas):
        return []
    return context.run('kafka', CHECKS, skip)
