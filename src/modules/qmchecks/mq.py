from modules.qmcore.aws import CheckContext, maximum, session_from_env


def configuration_revisions(ctx):
    values = []
    for configuration in ctx.call('mq', 'list_configurations', 'Configurations'):
        identifier = configuration.get('Id')
        if identifier:
            revisions = ctx.call('mq', 'list_configuration_revisions', 'Revisions',
                                 ConfigurationId=identifier)
            values.append((identifier, len(revisions), None))
    return maximum(values, 'MQConfiguration', 'mq:ListConfigurations+ListConfigurationRevisions')


CHECKS=[('L-4D525FD5','Number of brokers per region',lambda c:dict(usage=len(c.call('mq','list_brokers','BrokerSummaries')),source='mq:ListBrokers',method='ACCOUNT_COUNT')),
         ('L-5EF2BBC7', 'Revisions per configuration', configuration_revisions)]
def get_current_quotastatus_mq(session=None,*,ctx=None,skip=()):
 c=ctx or CheckContext(session or session_from_env()); return c.run('mq',CHECKS,skip) if any(s=='mq' for s,_ in c.quotas) else []
