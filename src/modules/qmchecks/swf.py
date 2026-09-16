"""Amazon Simple Workflow Service domain counts.

Workflow and activity types have separate listings, and counting open
executions needs an explicit start-time window.
"""
from datetime import timedelta

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

# SWF keeps an execution for at most a year, so a window of one year and a day
# cannot miss an execution that is still open.
EXECUTION_RETENTION = timedelta(days=366)


def workflow_types_per_domain(ctx):
    values = []
    for domain in ctx.call('swf', 'list_domains', 'domainInfos', registrationStatus='REGISTERED'):
        name = domain.get('name')
        if not name:
            continue
        total = 0
        for method in ('list_workflow_types', 'list_activity_types'):
            total += len(ctx.call('swf', method, 'typeInfos', domain=name,
                                  registrationStatus='REGISTERED'))
        values.append((name, total, None))
    return maximum(values, 'SWFDomain',
                   'swf:ListWorkflowTypes+ListActivityTypes')


def open_workflows_per_domain(ctx):
    values = []
    for domain in ctx.call('swf', 'list_domains', 'domainInfos', registrationStatus='REGISTERED'):
        name = domain.get('name')
        if name:
            result = ctx.call('swf', 'count_open_workflow_executions', domain=name,
                              startTimeFilter={'oldestDate':
                                               ctx.now - EXECUTION_RETENTION})
            if result.get('truncated'):
                raise NoData('SWF truncated the open execution count')
            values.append((name, result.get('count', 0), None))
    return maximum(values, 'SWFDomain', 'swf:CountOpenWorkflowExecutions')

CHECKS = [
    ('L-464CCB53', 'Registered domains',
     lambda c: dict(usage=len(c.call('swf', 'list_domains', 'domainInfos',
                                      registrationStatus='REGISTERED')),
                    source='swf:ListDomains', method='ACCOUNT_COUNT')),
    ('L-52C0BE72', 'Workflow and activity types per domain', workflow_types_per_domain),
    ('L-6FACB0D5', 'Open workflow executions per domain', open_workflows_per_domain),
]


def get_current_quotastatus_swf(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'swf' for service, _ in context.quotas):
        return []
    return context.run('swf', CHECKS, skip)
