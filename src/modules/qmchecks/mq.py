from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def configuration_revisions(ctx):
    values = []
    for configuration in ctx.call('mq', 'list_configurations', 'Configurations'):
        identifier = configuration.get('Id')
        if identifier:
            revisions = ctx.call('mq', 'list_configuration_revisions', 'Revisions',
                                 ConfigurationId=identifier)
            values.append((identifier, len(revisions), None))
    return maximum(values, 'MQConfiguration', 'mq:ListConfigurations+ListConfigurationRevisions')


def brokers(ctx):
    """Yield (broker id, detail) pairs.

    DescribeBroker carries the security groups, the tags and the users, and
    ctx.call caches it, so the three per-broker quotas share one request.
    """
    for summary in ctx.call('mq', 'list_brokers', 'BrokerSummaries'):
        identifier = summary.get('BrokerId')
        if not isinstance(identifier, str) or not identifier:
            raise NoData('Amazon MQ broker is missing its identity')
        detail = ctx.call('mq', 'describe_broker', BrokerId=identifier)
        if detail.get('BrokerId') != identifier:
            raise NoData('Amazon MQ broker detail has a different identity')
        yield identifier, detail


def per_broker(ctx, field):
    return maximum([(identifier, len(detail.get(field) or ()), None)
                    for identifier, detail in brokers(ctx)],
                   'MQBroker', 'mq:ListBrokers+DescribeBroker')


def simple_auth_users_per_broker(ctx):
    """Only a broker on simple authentication keeps users of its own."""
    return maximum([(identifier, len(detail.get('Users') or ()), None)
                    for identifier, detail in brokers(ctx)
                    if detail.get('AuthenticationStrategy') == 'SIMPLE'],
                   'MQBroker', 'mq:ListBrokers+DescribeBroker(SIMPLE)')


CHECKS=[('L-4D525FD5','Number of brokers per region',lambda c:dict(usage=len(c.call('mq','list_brokers','BrokerSummaries')),source='mq:ListBrokers',method='ACCOUNT_COUNT')),
         ('L-5EF2BBC7', 'Revisions per configuration', configuration_revisions),
         ('L-8113B3FA', 'Security groups per broker',
          lambda ctx: per_broker(ctx, 'SecurityGroups')),
         ('L-014B4583', 'Tags per broker', lambda ctx: per_broker(ctx, 'Tags')),
         ('L-D505D03E', 'Users per broker (simple auth)', simple_auth_users_per_broker)]
def get_current_quotastatus_mq(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('mq',CHECKS,skip) if any(s=='mq' for s,_ in c.quotas) else []
