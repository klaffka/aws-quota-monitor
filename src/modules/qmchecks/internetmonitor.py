"""Amazon CloudWatch Internet Monitor regional monitor counts."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resources_per_monitor(ctx):
    values = []
    for monitor in ctx.call('internetmonitor', 'list_monitors', 'Monitors'):
        name = monitor.get('MonitorName') or monitor.get('monitorName')
        if name:
            resources = ctx.call('internetmonitor', 'list_monitored_resources', 'MonitoredResources', MonitorName=name)
            values.append((name, len(resources), None))
    return maximum(values, 'Monitor', 'internetmonitor:ListMonitoredResources')

CHECKS = [('L-99A570F6', 'Monitors per account per AWS Region',
           lambda c: dict(usage=len(c.call('internetmonitor', 'list_monitors', 'Monitors')),
                          source='internetmonitor:ListMonitors', method='ACCOUNT_COUNT')),
          ('L-D43DFC35', 'Resources per monitor', resources_per_monitor)]


def get_current_quotastatus_internetmonitor(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'internetmonitor' for service, _ in context.quotas): return []
    return context.run('internetmonitor', CHECKS, skip)
