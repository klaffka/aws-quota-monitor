"""AWS Interconnect connection quotas."""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

INTERCONNECT = 'interconnect'
CONNECTION_STATES = {'available', 'requested', 'pending', 'down', 'deleting',
                     'deleted', 'failed', 'updating'}
# A deleted connection no longer occupies the account's connection quota.
GONE_STATES = {'deleted'}
REQUESTED_STATES = {'requested'}


def connections(ctx):
    found = {}
    for connection in ctx.call(INTERCONNECT, 'list_connections', 'connections'):
        identity = connection.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Interconnect connection is missing its identity')
        if connection.get('state') not in CONNECTION_STATES:
            raise NoData('Interconnect connection has an unknown state')
        found[identity] = connection
    return found


def _count(states=None, exclude=()):
    def check(ctx):
        usage = sum(connection['state'] in states if states is not None
                    else connection['state'] not in exclude
                    for connection in connections(ctx).values())
        return dict(usage=usage, source='interconnect:ListConnections',
                    method='ACCOUNT_COUNT')
    return check


def _per_provider(field, resource_type):
    """Group live connections by one side of their provider pair."""
    def check(ctx):
        counts = Counter()
        for connection in connections(ctx).values():
            if connection['state'] in GONE_STATES:
                continue
            provider = connection.get('provider')
            if not isinstance(provider, dict):
                raise NoData('Interconnect connection has no provider')
            name = provider.get(field)
            if name is None:
                continue
            if not isinstance(name, str) or not name:
                raise NoData('Interconnect provider has an invalid name')
            counts[name] += 1
        return maximum(((name, count, None) for name, count in counts.items()),
                       resource_type, 'interconnect:ListConnections')
    return check


CHECKS = [
    ('L-00139C4D', 'Interconnect Maximum Created Connections', _count(exclude=GONE_STATES)),
    ('L-29F85628', 'Interconnect Outstanding Requested Connections',
     _count(states=REQUESTED_STATES)),
    ('L-14D2B214', 'Last Mile Connections Per Provider',
     _per_provider('lastMileProvider', 'InterconnectLastMileProvider')),
    ('L-7B96960D', 'Multicloud Connections Per Provider',
     _per_provider('cloudServiceProvider', 'InterconnectCloudServiceProvider')),
]


def get_current_quotastatus_interconnect(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'interconnect' for service, _ in context.quotas):
        return []
    return context.run('interconnect', CHECKS, skip)
