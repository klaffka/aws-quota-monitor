"""AWS Direct Connect regional resource-count inventories."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('directconnect', method, key)),
                source=f'directconnect:{method}', method='ACCOUNT_COUNT')

def connections_per_location(ctx):
    from collections import Counter
    values = Counter(c.get('location') for c in ctx.call('directconnect', 'describe_connections', 'connections') if c.get('location'))
    return maximum([(location, count, None) for location, count in values.items()], 'DirectConnectLocation', 'directconnect:DescribeConnections')

def _interfaces_per_connection(ctx):
    """Yield (connection, its interface count) once for all three scopes."""
    for connection in ctx.call('directconnect', 'describe_connections', 'connections'):
        identity = connection.get('connectionId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Direct Connect connection is missing its identity')
        yield connection, len(ctx.call('directconnect', 'describe_virtual_interfaces',
                                       'virtualInterfaces', connectionId=identity))


def virtual_interfaces_per_connection(ctx):
    return maximum([(connection['connectionId'], count, None)
                    for connection, count in _interfaces_per_connection(ctx)],
                   'DirectConnectConnection', 'directconnect:DescribeVirtualInterfaces')


def interfaces_per_hosted_connection(ctx):
    """A connection a partner provisioned carries a partner name; a dedicated
    one does not, and holds a quota of its own."""
    return maximum([(connection['connectionId'], count, None)
                    for connection, count in _interfaces_per_connection(ctx)
                    if connection.get('partnerName')],
                   'DirectConnectConnection', 'directconnect:DescribeVirtualInterfaces')


def interfaces_per_lag(ctx):
    """A LAG bundles connections, so its interfaces are all of theirs."""
    counts = {}
    for connection, count in _interfaces_per_connection(ctx):
        lag = connection.get('lagId')
        if lag:
            counts[lag] = counts.get(lag, 0) + count
    return maximum([(lag, count, None) for lag, count in sorted(counts.items())],
                   'DirectConnectLag', 'directconnect:DescribeVirtualInterfaces')


CHECKS = [
    ('L-62B7491E', 'Direct Connect gateways per account',
     lambda ctx: count(ctx, 'describe_direct_connect_gateways', 'directConnectGateways')),
    ('L-42DEC0EF', 'LAGs per Region', lambda ctx: count(ctx, 'describe_lags', 'lags')),
    ('L-A2659207', 'Dedicated connections per location', connections_per_location),
    ('L-53A26B6D', 'Total virtual interfaces per dedicated connection', virtual_interfaces_per_connection),
    ('L-3745876E', 'Private or public or transit virtual interfaces per hosted connection',
     interfaces_per_hosted_connection),
    ('L-59AD3548', 'Virtual interfaces per LAG', interfaces_per_lag),
]


def get_current_quotastatus_directconnect(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'directconnect' for service, _ in context.quotas):
        return []
    return context.run('directconnect', CHECKS, skip)
