from unittest.mock import Mock

from modules.qmchecks.pinpoint import (active_campaigns, active_in_app_campaigns_per_project,
                                       active_journeys, projects, template_versions_per_template)


def test_pinpoint_projects_read_nested_get_apps_response():
    ctx = Mock()
    ctx.call.return_value = {
        'ApplicationsResponse': {'Item': [{'Id': 'one'}, {'Id': 'two'}]}}
    assert len(projects(ctx)) == 2
    assert ctx.call.call_args.args[:2] == ('pinpoint', 'get_apps')


def test_pinpoint_active_campaigns_and_journeys_cover_all_apps_and_pages():
    # Pinpoint sends the next page token back as `Token`, not `NextToken`.
    ctx = Mock()

    def call(_service, method, **kwargs):
        if method == 'get_apps':
            return {'ApplicationsResponse': {'Item': [{'Id': 'one'}, {'Id': 'two'}]}}
        if method == 'get_campaigns':
            if kwargs.get('ApplicationId') == 'one' and 'Token' not in kwargs:
                return {'CampaignsResponse': {'Item': [{'State': 'ACTIVE'}], 'NextToken': 'next'}}
            if kwargs.get('ApplicationId') == 'one':
                return {'CampaignsResponse': {'Item': [{'State': 'COMPLETED'}]}}
            return {'CampaignsResponse': {'Item': [{'State': 'ACTIVE'}, {'State': 'DRAFT'}]}}
        if method == 'list_journeys':
            return {'JourneysResponse': {'Item': [{'State': 'ACTIVE'}]}}
        raise AssertionError(method)

    ctx.call.side_effect = call
    assert active_campaigns(ctx) == 2
    assert active_journeys(ctx) == 2


def test_pinpoint_active_in_app_campaigns_are_maximum_per_project():
    ctx = Mock()

    def call(_service, method, **kwargs):
        if method == 'get_apps':
            return {'ApplicationsResponse': {'Item': [{'Id': 'one'}, {'Id': 'two'}]}}
        if kwargs['ApplicationId'] == 'one':
            return {'CampaignsResponse': {'Item': [
                {'State': 'ACTIVE', 'MessageConfiguration': {'InAppMessage': {}}},
                {'State': 'ACTIVE', 'MessageConfiguration': {'EmailMessage': {}}},
            ]}}
        return {'CampaignsResponse': {'Item': [
            {'State': 'ACTIVE', 'MessageConfiguration': {'InAppMessage': {}}},
            {'State': 'ACTIVE', 'InAppMessage': {}},
            {'State': 'DRAFT', 'MessageConfiguration': {'InAppMessage': {}}},
        ]}}

    ctx.call.side_effect = call
    assert active_in_app_campaigns_per_project(ctx)['usage'] == 2


def test_pinpoint_template_versions_are_maximum_per_template():
    ctx = Mock()

    def call(_service, method, **kwargs):
        if method == 'list_templates':
            if kwargs['TemplateType'] == 'EMAIL':
                return {'TemplatesResponse': {'Item': [
                    {'TemplateName': 'small'}, {'TemplateName': 'large'}]}}
            return {'TemplatesResponse': {'Item': []}}
        if method == 'list_template_versions':
            count = 3 if kwargs['TemplateName'] == 'large' else 1
            return {'TemplateVersionsResponse': {'Item': [{}] * count}}
        raise AssertionError(method)

    ctx.call.side_effect = call
    assert template_versions_per_template(ctx)['usage'] == 3
