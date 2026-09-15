"""Compute Optimizer automation event concurrency quota."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

AUTOMATION = 'compute-optimizer-automation'
EVENT_STATES = {'Ready', 'InProgress', 'Complete', 'Failed', 'Cancelled',
                'RollbackReady', 'RollbackInProgress', 'RollbackComplete',
                'RollbackFailed'}
RUNNING_STATES = {'InProgress', 'RollbackInProgress'}


def executing_events(ctx):
    usage = 0
    for event in ctx.call(AUTOMATION, 'list_automation_events', 'automationEvents'):
        status = event.get('eventStatus')
        if status not in EVENT_STATES:
            raise NoData('Automation event has an unknown status')
        usage += status in RUNNING_STATES
    return dict(usage=usage,
                source='compute-optimizer-automation:ListAutomationEvents',
                method='ACCOUNT_COUNT')


CHECKS = [('L-E486B777', 'Concurrently executing automation events per account',
           executing_events)]


def get_current_quotastatus_aco_automation(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'aco-automation' for service, _ in context.quotas):
        return []
    return context.run('aco-automation', CHECKS, skip)
