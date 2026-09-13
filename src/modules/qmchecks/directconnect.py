"""AWS Direct Connect regional resource-count inventories."""
from modules.qmcore.aws import CheckContext, session_from_env, maximum


def count(ctx, method, key):
    return dict(usage=len(ctx.call('directconnect', method, key)),
                source=f'directconnect:{method}', method='ACCOUNT_COUNT')

def connections_per_location(ctx):
    from collections import Counter
    values = Counter(c.get('location') for c in ctx.call('directconnect', 'describe_connections', 'connections') if c.get('location'))
    return maximum([(location, count, None) for location, count in values.items()], 'DirectConnectLocation', 'directconnect:DescribeConnections')

def virtual_interfaces_per_connection(ctx):
    values = []
    for connection in ctx.call('directconnect', 'describe_connections', 'connections'):
        cid = connection.get('connectionId')
        if cid:
            values.append((cid, len(ctx.call('directconnect', 'describe_virtual_interfaces', 'virtualInterfaces', connectionId=cid)), None))
    return maximum(values, 'DirectConnectConnection', 'directconnect:DescribeVirtualInterfaces')


CHECKS = [
    ('L-62B7491E', 'Direct Connect gateways per account',
     lambda ctx: count(ctx, 'describe_direct_connect_gateways', 'directConnectGateways')),
    ('L-42DEC0EF', 'LAGs per Region', lambda ctx: count(ctx, 'describe_lags', 'lags')),
    ('L-A2659207', 'Dedicated connections per location', connections_per_location),
    ('L-53A26B6D', 'Total virtual interfaces per dedicated connection', virtual_interfaces_per_connection),
]


def get_current_quotastatus_directconnect(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'directconnect' for service, _ in context.quotas):
        return []
    return context.run('directconnect', CHECKS, skip)
