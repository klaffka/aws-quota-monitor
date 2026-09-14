"""Migration Hub Refactor Spaces account/Region resource quotas."""

from modules.qmcore.aws import CheckContext, NoData, session_from_env


SERVICE = 'migration-hub-refactor-spaces'
STATES = {
    'environment': {'CREATING', 'ACTIVE', 'DELETING', 'FAILED'},
    'application': {'CREATING', 'ACTIVE', 'DELETING', 'FAILED', 'UPDATING'},
    'service': {'CREATING', 'ACTIVE', 'DELETING', 'FAILED'},
    'route': {'CREATING', 'ACTIVE', 'DELETING', 'FAILED', 'UPDATING', 'INACTIVE'},
}


def _validated(items, identity_field, subject, *, parents=()):
    result = []
    identities = set()
    for item in items:
        if not isinstance(item, dict):
            raise NoData(f'Refactor Spaces {subject} inventory contains an invalid item')
        identity = item.get(identity_field)
        arn = item.get('Arn')
        owner = item.get('OwnerAccountId')
        if (not isinstance(identity, str) or not identity
                or not isinstance(arn, str) or not arn
                or not isinstance(owner, str) or not owner
                or item.get('State') not in STATES[subject]):
            raise NoData(f'Refactor Spaces {subject} is missing required identity data')
        if any(item.get(field) != value for field, value in parents):
            raise NoData(f'Refactor Spaces {subject} has an inconsistent parent')
        if identity in identities:
            raise NoData(f'Refactor Spaces {subject} inventory contains a duplicate')
        identities.add(identity)
        result.append(item)
    return result


def environments(ctx):
    return _validated(
        ctx.call(SERVICE, 'list_environments', 'EnvironmentSummaryList'),
        'EnvironmentId', 'environment')


def applications(ctx):
    result = []
    identities = set()
    for environment in environments(ctx):
        environment_id = environment['EnvironmentId']
        items = _validated(
            ctx.call(SERVICE, 'list_applications', 'ApplicationSummaryList',
                     EnvironmentIdentifier=environment_id),
            'ApplicationId', 'application', parents=(('EnvironmentId', environment_id),))
        for item in items:
            if item['ApplicationId'] in identities:
                raise NoData('Refactor Spaces application inventory contains a duplicate')
            identities.add(item['ApplicationId'])
            result.append(item)
    return result


def services(ctx):
    result = []
    identities = set()
    for application in applications(ctx):
        environment_id = application['EnvironmentId']
        application_id = application['ApplicationId']
        items = _validated(
            ctx.call(SERVICE, 'list_services', 'ServiceSummaryList',
                     EnvironmentIdentifier=environment_id,
                     ApplicationIdentifier=application_id),
            'ServiceId', 'service',
            parents=(('EnvironmentId', environment_id),
                     ('ApplicationId', application_id)))
        for item in items:
            if item['ServiceId'] in identities:
                raise NoData('Refactor Spaces service inventory contains a duplicate')
            identities.add(item['ServiceId'])
            result.append(item)
    return result


def routes(ctx):
    result = []
    identities = set()
    for application in applications(ctx):
        environment_id = application['EnvironmentId']
        application_id = application['ApplicationId']
        items = _validated(
            ctx.call(SERVICE, 'list_routes', 'RouteSummaryList',
                     EnvironmentIdentifier=environment_id,
                     ApplicationIdentifier=application_id),
            'RouteId', 'route',
            parents=(('EnvironmentId', environment_id),
                     ('ApplicationId', application_id)))
        for item in items:
            if item['RouteId'] in identities:
                raise NoData('Refactor Spaces route inventory contains a duplicate')
            identities.add(item['RouteId'])
            result.append(item)
    return result


def owned_count(ctx, inventory, source):
    return dict(usage=sum(item['OwnerAccountId'] == ctx.account
                          for item in inventory(ctx)),
                source=source, method='ACCOUNT_COUNT')


CHECKS = [
    ('L-DEF84811', 'Environments',
     lambda ctx: owned_count(ctx, environments, f'{SERVICE}:ListEnvironments')),
    ('L-EACEDE8E', 'Applications',
     lambda ctx: owned_count(ctx, applications, f'{SERVICE}:ListApplications')),
    ('L-B19E8A2B', 'Services',
     lambda ctx: owned_count(ctx, services, f'{SERVICE}:ListServices')),
    ('L-CE52EEA2', 'Routes',
     lambda ctx: owned_count(ctx, routes, f'{SERVICE}:ListRoutes')),
]


def get_current_quotastatus_refactor_spaces(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'refactor-spaces' for service, _ in context.quotas):
        return []
    return context.run('refactor-spaces', CHECKS, skip)
