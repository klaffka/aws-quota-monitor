"""AWS Launch Wizard deployment quotas.

`Settings Set` counts saved deployment settings, which the API does not list,
so it is not measured here.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

LAUNCH_WIZARD = 'launch-wizard'
DEPLOYMENT_STATES = {
    'COMPLETED', 'CREATING', 'DELETE_IN_PROGRESS', 'DELETE_INITIATING',
    'DELETE_FAILED', 'DELETED', 'FAILED', 'IN_PROGRESS', 'VALIDATING',
    'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETED', 'UPDATE_FAILED',
    'UPDATE_ROLLBACK_COMPLETED', 'UPDATE_ROLLBACK_FAILED',
}
# A deleted deployment no longer occupies the account's deployment quota.
GONE_STATES = {'DELETED'}
IN_PROGRESS_STATES = {'CREATING', 'IN_PROGRESS', 'VALIDATING', 'UPDATE_IN_PROGRESS',
                      'DELETE_IN_PROGRESS', 'DELETE_INITIATING'}


def deployments(ctx):
    found = {}
    for deployment in ctx.call(LAUNCH_WIZARD, 'list_deployments', 'deployments'):
        identity = deployment.get('id')
        if not isinstance(identity, str) or not identity:
            raise NoData('Launch Wizard deployment is missing its identity')
        if deployment.get('status') not in DEPLOYMENT_STATES:
            raise NoData('Launch Wizard deployment has an unknown status')
        found[identity] = deployment
    return found


def _count(states=None, exclude=()):
    def check(ctx):
        usage = sum(deployment['status'] in states if states is not None
                    else deployment['status'] not in exclude
                    for deployment in deployments(ctx).values())
        return dict(usage=usage, source='launch-wizard:ListDeployments',
                    method='ACCOUNT_COUNT')
    return check


CHECKS = [
    ('L-067B0AC5', 'Deployments', _count(exclude=GONE_STATES)),
    ('L-E64920AC', 'Active deployments', _count(exclude=GONE_STATES | {'FAILED'})),
    ('L-0DE2E185', 'In-Progress Deployments', _count(states=IN_PROGRESS_STATES)),
]


def get_current_quotastatus_launchwizard(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'launchwizard' for service, _ in context.quotas):
        return []
    return context.run('launchwizard', CHECKS, skip)
