"""AWS CodeDeploy application, deployment group and deployment quotas.

The duration, timing and traffic-shift quotas bound one deployment's behaviour
rather than an inventory, and the instance counts a deployment reaches are
reported per deployment target rather than per account.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CODEDEPLOY = 'codedeploy'
RUNNING_STATES = ['Created', 'Queued', 'InProgress', 'Baking', 'Ready']
# AWS ships its own deployment configurations under this prefix.
BUILT_IN_PREFIX = 'CodeDeployDefault'


def applications(ctx):
    found = []
    for name in ctx.call(CODEDEPLOY, 'list_applications', 'applications'):
        if not isinstance(name, str) or not name:
            raise NoData('CodeDeploy application is missing its name')
        if name not in found:
            found.append(name)
    return found


def deployment_groups(application, ctx):
    found = []
    for name in ctx.call(CODEDEPLOY, 'list_deployment_groups', 'deploymentGroups',
                         applicationName=application):
        if not isinstance(name, str) or not name:
            raise NoData('CodeDeploy deployment group is missing its name')
        found.append(name)
    return found


def deployment_groups_per_application(ctx):
    values = [(application, len(deployment_groups(application, ctx)), None)
              for application in applications(ctx)]
    return maximum(values, 'Application', 'codedeploy:ListDeploymentGroups')


def _group_details(ctx):
    for application in applications(ctx):
        for name in deployment_groups(application, ctx):
            detail = ctx.call(CODEDEPLOY, 'get_deployment_group',
                              applicationName=application,
                              deploymentGroupName=name).get('deploymentGroupInfo')
            if not isinstance(detail, dict):
                raise NoData('CodeDeploy deployment group has no detail')
            yield f'{application}/{name}', detail


def _group_maximum(field, subject):
    """Report the largest configured list on any deployment group."""
    def check(ctx):
        values = []
        for identity, detail in _group_details(ctx):
            entries = detail.get(field) or []
            if not isinstance(entries, list):
                raise NoData(f'CodeDeploy deployment group has an invalid {subject}')
            values.append((identity, len(entries), None))
        return maximum(values, 'DeploymentGroup', 'codedeploy:GetDeploymentGroup')
    return check


def alarms_per_deployment_group(ctx):
    values = []
    for identity, detail in _group_details(ctx):
        configuration = detail.get('alarmConfiguration') or {}
        alarms = configuration.get('alarms') or []
        if not isinstance(alarms, list):
            raise NoData('CodeDeploy deployment group has an invalid alarm list')
        values.append((identity, len(alarms), None))
    return maximum(values, 'DeploymentGroup', 'codedeploy:GetDeploymentGroup')


def deployment_groups_per_ecs_service(ctx):
    counts = Counter()
    for _, detail in _group_details(ctx):
        for service in detail.get('ecsServices') or []:
            cluster = service.get('clusterName') if isinstance(service, dict) else None
            name = service.get('serviceName') if isinstance(service, dict) else None
            if not isinstance(cluster, str) or not isinstance(name, str):
                raise NoData('CodeDeploy ECS service reference is incomplete')
            counts[f'{cluster}/{name}'] += 1
    return maximum(((service, count, None) for service, count in counts.items()),
                   'ECSService', 'codedeploy:GetDeploymentGroup')


def custom_deployment_configurations(ctx):
    usage = 0
    for name in ctx.call(CODEDEPLOY, 'list_deployment_configs', 'deploymentConfigsList'):
        if not isinstance(name, str) or not name:
            raise NoData('CodeDeploy deployment configuration is missing its name')
        usage += not name.startswith(BUILT_IN_PREFIX)
    return dict(usage=usage, source='codedeploy:ListDeploymentConfigs',
                method='ACCOUNT_COUNT')


def concurrent_deployments(ctx):
    usage = len(ctx.call(CODEDEPLOY, 'list_deployments', 'deployments',
                         includeOnlyStatuses=RUNNING_STATES))
    return dict(usage=usage, source='codedeploy:ListDeployments',
                method='ACCOUNT_COUNT')


def concurrent_deployments_per_group(ctx):
    values = []
    for application in applications(ctx):
        for name in deployment_groups(application, ctx):
            running = ctx.call(CODEDEPLOY, 'list_deployments', 'deployments',
                               applicationName=application, deploymentGroupName=name,
                               includeOnlyStatuses=RUNNING_STATES)
            values.append((f'{application}/{name}', len(running), None))
    return maximum(values, 'DeploymentGroup', 'codedeploy:ListDeployments')


CHECKS = [
    ('L-3F19B6A5', 'Applications associated per account per region',
     lambda ctx: dict(usage=len(applications(ctx)),
                      source='codedeploy:ListApplications', method='ACCOUNT_COUNT')),
    ('L-D9088B77', 'Deployment groups associated with a single application',
     deployment_groups_per_application),
    ('L-9F835576', 'Associated alarms per deployment group', alarms_per_deployment_group),
    ('L-6DACB4EE', 'Auto Scaling groups in a deployment group',
     _group_maximum('autoScalingGroups', 'Auto Scaling group list')),
    ('L-877B748B', 'Event notification triggers in a deployment group',
     _group_maximum('triggerConfigurations', 'trigger list')),
    ('L-0CB3C26F', 'Number of deployment groups that can be associated with an '
                   'Amazon ECS service', deployment_groups_per_ecs_service),
    ('L-5AD34096', 'Custom deployment configurations per account',
     custom_deployment_configurations),
    ('L-AB125F0B', 'Concurrent deployments per account', concurrent_deployments),
    ('L-A8B8B32B', 'Concurrent deployments per deployment group',
     concurrent_deployments_per_group),
]


def get_current_quotastatus_codedeploy(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codedeploy' for service, _ in context.quotas):
        return []
    return context.run('codedeploy', CHECKS, skip)
