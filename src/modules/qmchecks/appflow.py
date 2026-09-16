"""Amazon AppFlow flow and connector profile inventories.

The flow run size, event size and record quotas bound a single run or record,
the per-connector flow run quotas are rates, and concurrent and monthly flow
runs count executions that `ListFlows` does not expose.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

APPFLOW = 'appflow'


def _unique(ctx, method, key, field, subject):
    found = set()
    for item in ctx.call(APPFLOW, method, key):
        identity = item.get(field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'AppFlow {subject} is missing its name')
        found.add(identity)
    return found


CHECKS = [
    ('L-A847D5B6', 'Total flows',
     lambda ctx: dict(usage=len(_unique(ctx, 'list_flows', 'flows', 'flowName', 'flow')),
                      source='appflow:ListFlows', method='ACCOUNT_COUNT')),
    ('L-0F8AA170', 'Connector profiles',
     lambda ctx: dict(usage=len(_unique(ctx, 'describe_connector_profiles',
                                        'connectorProfileDetails',
                                        'connectorProfileName', 'connector profile')),
                      source='appflow:DescribeConnectorProfiles',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_appflow(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appflow' for service, _ in context.quotas):
        return []
    return context.run('appflow', CHECKS, skip)
