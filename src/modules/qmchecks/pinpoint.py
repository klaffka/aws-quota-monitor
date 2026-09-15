"""Amazon Pinpoint project, campaign, journey and import job quotas.

The attribute and parameter quotas bound one request or one endpoint record,
and the sending quotas meter a rolling 24-hour period.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

PINPOINT = 'pinpoint'
IMPORT_JOB_STATES = {'CREATED', 'PREPARING_FOR_INITIALIZATION', 'INITIALIZING',
                     'PROCESSING', 'PENDING_JOB', 'COMPLETING', 'COMPLETED',
                     'FAILING', 'FAILED'}
RUNNING_IMPORT_STATES = {'CREATED', 'PREPARING_FOR_INITIALIZATION', 'INITIALIZING',
                         'PROCESSING', 'PENDING_JOB', 'COMPLETING'}


def _pages(ctx, method, response_key, **arguments):
    """Read all Pinpoint pages, whose item lists are nested in response objects.

    Every Pinpoint listing takes the page token as `Token` and returns the next
    one as `NextToken`, so the two names cannot be used interchangeably.
    """
    items, token = [], None
    while True:
        kwargs = dict(arguments)
        if token:
            kwargs['Token'] = token
        response = ctx.call(PINPOINT, method, **kwargs)
        nested = response.get(response_key, {})
        items.extend(nested.get('Item', []))
        new_token = nested.get('NextToken')
        if not new_token or new_token == token:
            return items
        token = new_token


def projects(ctx):
    return _pages(ctx, 'get_apps', 'ApplicationsResponse')


def _items(ctx, method, response_key, application_id):
    return _pages(ctx, method, response_key, ApplicationId=application_id)


def active_campaigns(ctx):
    return sum(sum(campaign.get('State') == 'ACTIVE'
                   for campaign in _items(ctx, 'get_campaigns', 'CampaignsResponse', app['Id']))
               for app in projects(ctx))


def active_in_app_campaigns_per_project(ctx):
    """Return the largest active in-app campaign count for one project."""
    values = []
    for app in projects(ctx):
        app_id = app.get('Id')
        if not app_id:
            continue
        campaigns = _items(ctx, 'get_campaigns', 'CampaignsResponse', app_id)
        count = sum(
            campaign.get('State') == 'ACTIVE'
            and ('InAppMessage' in (campaign.get('MessageConfiguration') or {})
                 or 'InAppMessage' in campaign)
            for campaign in campaigns)
        values.append((app_id, count, None))
    return maximum(values, 'PinpointProject', 'pinpoint:GetApps+GetCampaigns')


def active_journeys(ctx):
    return sum(sum(journey.get('State') == 'ACTIVE'
                   for journey in _items(ctx, 'list_journeys', 'JourneysResponse', app['Id']))
               for app in projects(ctx))


def concurrent_import_jobs(ctx):
    usage = 0
    for app in projects(ctx):
        for job in _items(ctx, 'get_import_jobs', 'ImportJobsResponse', app['Id']):
            status = job.get('JobStatus')
            if status not in IMPORT_JOB_STATES:
                raise NoData('Pinpoint import job has an unknown status')
            usage += status in RUNNING_IMPORT_STATES
    return dict(usage=usage, source='pinpoint:GetApps+GetImportJobs',
                method='ACCOUNT_COUNT')


def event_based_campaigns(ctx):
    """A campaign is event based when its schedule carries an event filter."""
    usage = 0
    for app in projects(ctx):
        for campaign in _items(ctx, 'get_campaigns', 'CampaignsResponse', app['Id']):
            schedule = campaign.get('Schedule') or {}
            usage += bool(schedule.get('EventFilter'))
    return dict(usage=usage, source='pinpoint:GetApps+GetCampaigns',
                method='ACCOUNT_COUNT')


def active_event_triggered_journeys(ctx):
    usage = 0
    for app in projects(ctx):
        for journey in _items(ctx, 'list_journeys', 'JourneysResponse', app['Id']):
            condition = journey.get('StartCondition') or {}
            usage += (journey.get('State') == 'ACTIVE'
                      and bool(condition.get('EventStartCondition')))
    return dict(usage=usage, source='pinpoint:GetApps+ListJourneys',
                method='ACCOUNT_COUNT')


def activities_per_journey(ctx):
    values = []
    for app in projects(ctx):
        for journey in _items(ctx, 'list_journeys', 'JourneysResponse', app['Id']):
            identity = journey.get('Id')
            if not isinstance(identity, str) or not identity:
                raise NoData('Pinpoint journey is missing its identity')
            activities = journey.get('Activities') or {}
            if not isinstance(activities, dict):
                raise NoData('Pinpoint journey has an invalid activity map')
            values.append((identity, len(activities), None))
    return maximum(values, 'PinpointJourney', 'pinpoint:ListJourneys')


def _templates(ctx):
    total = 0
    for template_type in ('EMAIL', 'SMS', 'VOICE', 'PUSH', 'INAPP'):
        token, count = None, 0
        while True:
            kwargs = {'TemplateType': template_type}
            if token:
                kwargs['NextToken'] = token
            response = ctx.call('pinpoint', 'list_templates', **kwargs)
            nested = response.get('TemplatesResponse', {})
            count += len(nested.get('Item', []))
            new_token = nested.get('NextToken')
            if not new_token or new_token == token:
                break
            token = new_token
        total += count
    return total


def template_versions_per_template(ctx):
    """Return the largest version count for any Pinpoint message template."""
    values = []
    for template_type in ('EMAIL', 'SMS', 'VOICE', 'PUSH', 'INAPP'):
        token = None
        while True:
            kwargs = {'TemplateType': template_type}
            if token:
                kwargs['NextToken'] = token
            response = ctx.call('pinpoint', 'list_templates', **kwargs)
            nested = response.get('TemplatesResponse', {})
            for template in nested.get('Item', []):
                name = template.get('TemplateName')
                if not name:
                    continue
                versions_token, versions = None, []
                while True:
                    version_kwargs = {'TemplateName': name, 'TemplateType': template_type}
                    if versions_token:
                        version_kwargs['NextToken'] = versions_token
                    version_response = ctx.call('pinpoint', 'list_template_versions',
                                                **version_kwargs)
                    version_nested = version_response.get('TemplateVersionsResponse', {})
                    versions.extend(version_nested.get('Item', []))
                    new_token = version_nested.get('NextToken')
                    if not new_token or new_token == versions_token:
                        break
                    versions_token = new_token
                values.append((f'{template_type}:{name}', len(versions), None))
            new_token = nested.get('NextToken')
            if not new_token or new_token == token:
                break
            token = new_token
    return maximum(values, 'PinpointTemplate', 'pinpoint:ListTemplates+ListTemplateVersions')


CHECKS = [
    ('L-9657965F', 'Number of Amazon Pinpoint projects',
     lambda ctx: dict(usage=len(projects(ctx)), source='pinpoint:GetApps', method='ACCOUNT_COUNT')),
    ('L-75AFB9F3', 'Active campaigns per account',
     lambda ctx: dict(usage=active_campaigns(ctx), source='pinpoint:GetApps+GetCampaigns', method='ACCOUNT_COUNT')),
    ('L-D9507B3D', 'Maximum number of active journeys per account',
     lambda ctx: dict(usage=active_journeys(ctx), source='pinpoint:GetApps+ListJourneys', method='ACCOUNT_COUNT')),
    ('L-EF46E894', 'Maximum number of message templates per account',
     lambda ctx: dict(usage=_templates(ctx), source='pinpoint:ListTemplates', method='ACCOUNT_COUNT')),
    ('L-2555226F', 'Maximum number of versions per template', template_versions_per_template),
    ('L-952D08C7', 'Active in-app campaigns per project', active_in_app_campaigns_per_project),
    ('L-4BC0A2FD', 'Number of concurrent import jobs', concurrent_import_jobs),
    ('L-CC53764D', 'Number of event-based campaigns', event_based_campaigns),
    ('L-692A3DD2', 'Maximum number of active event triggered journeys per account',
     active_event_triggered_journeys),
    ('L-08122D1D', 'Maximum number of journey activities per journey',
     activities_per_journey),
]


def get_current_quotastatus_pinpoint(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'pinpoint' for service, _ in context.quotas):
        return []
    return context.run('pinpoint', CHECKS, skip)
