"""Amazon Pinpoint regional project resource quota."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def projects(ctx):
    response = ctx.call('pinpoint', 'get_apps')
    return response.get('ApplicationsResponse', {}).get('Item', [])


def _items(ctx, method, response_key, application_id):
    """Read all Pinpoint pages, whose item lists are nested in response objects."""
    items, token = [], None
    while True:
        kwargs = {'ApplicationId': application_id}
        if token:
            kwargs['NextToken'] = token
        response = ctx.call('pinpoint', method, **kwargs)
        nested = response.get(response_key, {})
        items.extend(nested.get('Item', []))
        new_token = nested.get('NextToken')
        if not new_token or new_token == token:
            return items
        token = new_token


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
                   for journey in _items(ctx, 'get_journeys', 'JourneysResponse', app['Id']))
               for app in projects(ctx))


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
     lambda ctx: dict(usage=active_journeys(ctx), source='pinpoint:GetApps+GetJourneys', method='ACCOUNT_COUNT')),
    ('L-EF46E894', 'Maximum number of message templates per account',
     lambda ctx: dict(usage=_templates(ctx), source='pinpoint:ListTemplates', method='ACCOUNT_COUNT')),
    ('L-2555226F', 'Maximum number of versions per template', template_versions_per_template),
    ('L-952D08C7', 'Active in-app campaigns per project', active_in_app_campaigns_per_project),
]


def get_current_quotastatus_pinpoint(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'pinpoint' for service, _ in context.quotas):
        return []
    return context.run('pinpoint', CHECKS, skip)
