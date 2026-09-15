"""Amazon CloudWatch Internet Monitor regional monitor counts.

A monitor's resources are only returned by `GetMonitor`; the service has no
listing operation for them.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

INTERNETMONITOR = 'internetmonitor'


def monitors(ctx):
    found = []
    for monitor in ctx.call(INTERNETMONITOR, 'list_monitors', 'Monitors'):
        name = monitor.get('MonitorName')
        if not isinstance(name, str) or not name:
            raise NoData('Internet Monitor monitor is missing its name')
        found.append(name)
    return found


def resources_per_monitor(ctx):
    values = []
    for name in monitors(ctx):
        detail = ctx.call(INTERNETMONITOR, 'get_monitor', MonitorName=name)
        if detail.get('MonitorName') != name:
            raise NoData('Internet Monitor answered for a different monitor')
        resources = detail.get('Resources')
        if not isinstance(resources, list):
            raise NoData('Internet Monitor monitor has no resource list')
        values.append((name, len(resources), None))
    return maximum(values, 'Monitor', 'internetmonitor:GetMonitor')


CHECKS = [
    ('L-99A570F6', 'Monitors per account per AWS Region',
     lambda ctx: dict(usage=len(monitors(ctx)),
                      source='internetmonitor:ListMonitors', method='ACCOUNT_COUNT')),
    ('L-D43DFC35', 'Resources per monitor', resources_per_monitor),
]


def get_current_quotastatus_internetmonitor(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == INTERNETMONITOR for service, _ in context.quotas):
        return []
    return context.run(INTERNETMONITOR, CHECKS, skip)
