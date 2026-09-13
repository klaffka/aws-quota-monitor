"""Amazon EVS environment and host inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def hosts_per_environment(ctx):
    values = []
    for env in ctx.call('evs', 'list_environments', 'environments'):
        identifier = env.get('environmentId')
        if identifier:
            values.append((identifier, len(ctx.call('evs', 'list_environment_hosts', 'hosts',
                                                   environmentId=identifier)), None))
    return maximum(values, 'EVSEnvironment', 'evs:ListEnvironmentHosts')


CHECKS = [
    ('L-27E780D9', 'Environment count per AWS account',
     lambda c: dict(usage=len(c.call('evs', 'list_environments', 'environments')),
                    source='evs:ListEnvironments', method='ACCOUNT_COUNT')),
    ('L-96A49955', 'Host count per EVS environment', hosts_per_environment),
]


def get_current_quotastatus_evs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'evs' for service, _ in context.quotas):
        return []
    return context.run('evs', CHECKS, skip)
