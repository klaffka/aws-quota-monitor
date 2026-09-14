from pathlib import Path

import pytest

from modules.qmchecks.pca_connector_ad import (
    CHECKS,
    access_entries_per_template,
    connector_count,
    connectors,
    templates,
    templates_per_connector,
)
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '111111111111'
REGION = 'eu-central-1'
SERVICE = 'pca-connector-ad'


def connector(identity, **values):
    return {'Arn': f'arn:aws:{SERVICE}:{REGION}:{ACCOUNT}:connector/{identity}',
            'Status': 'ACTIVE', **values}


def template(connector_arn, identity, **values):
    return {'Arn': f'{connector_arn}/template/{identity}',
            'ConnectorArn': connector_arn, 'Status': 'ACTIVE', **values}


def entry(template_arn, sid, **values):
    return {'TemplateArn': template_arn, 'GroupSecurityIdentifier': sid, **values}


class Context:
    account = ACCOUNT
    region = REGION

    def __init__(self):
        self.connectors = [connector('connector-one'), connector('connector-two')]
        first, second = (item['Arn'] for item in self.connectors)
        self.templates = {
            first: [template(first, 'template-one'), template(first, 'template-two')],
            second: [template(second, 'template-three')],
        }
        self.entries = {
            self.templates[first][0]['Arn']: [
                entry(self.templates[first][0]['Arn'], 'S-1-1'),
                entry(self.templates[first][0]['Arn'], 'S-1-2')],
            self.templates[first][1]['Arn']: [],
            self.templates[second][0]['Arn']: [
                entry(self.templates[second][0]['Arn'], 'S-1-3')],
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == SERVICE
        if method == 'list_connectors':
            return self.connectors
        if method == 'list_templates':
            return self.templates[kwargs['ConnectorArn']]
        if method == 'list_template_group_access_control_entries':
            return self.entries[kwargs['TemplateArn']]
        raise AssertionError((method, key, kwargs))


def test_pca_connector_ad_counts_all_three_resource_scopes():
    ctx = Context()
    assert connector_count(ctx)['usage'] == 2
    assert templates_per_connector(ctx)['usage'] == 2
    assert access_entries_per_template(ctx)['usage'] == 2


def test_pca_connector_ad_deduplicates_identical_repeated_pages():
    ctx = Context()
    ctx.connectors.append(dict(ctx.connectors[0]))
    first = ctx.connectors[0]['Arn']
    ctx.templates[first].append(dict(ctx.templates[first][0]))
    template_arn = ctx.templates[first][0]['Arn']
    ctx.entries[template_arn].append(dict(ctx.entries[template_arn][0]))
    assert len(connectors(ctx)) == 2
    assert len(templates(ctx)[1]) == 3
    assert access_entries_per_template(ctx)['usage'] == 2


def test_pca_connector_ad_rejects_invalid_connector_identity_or_state():
    ctx = Context()
    ctx.connectors[0]['Arn'] = ctx.connectors[0]['Arn'].replace(REGION, 'eu-west-1')
    with pytest.raises(NoData, match='inconsistent ARN'):
        connectors(ctx)

    ctx = Context()
    ctx.connectors[0]['Status'] = 'FUTURE'
    with pytest.raises(NoData, match='unknown state'):
        connectors(ctx)


def test_pca_connector_ad_rejects_invalid_template_parent_and_conflicts():
    ctx = Context()
    first = ctx.connectors[0]['Arn']
    ctx.templates[first][0]['ConnectorArn'] = ctx.connectors[1]['Arn']
    with pytest.raises(NoData, match='parent or state'):
        templates(ctx)

    ctx = Context()
    first = ctx.connectors[0]['Arn']
    ctx.templates[first].append(dict(ctx.templates[first][0], Name='changed'))
    with pytest.raises(NoData, match='changed during pagination'):
        templates(ctx)


def test_pca_connector_ad_rejects_invalid_access_entry_parent_and_conflicts():
    ctx = Context()
    first = ctx.connectors[0]['Arn']
    template_arn = ctx.templates[first][0]['Arn']
    ctx.entries[template_arn][0]['TemplateArn'] = ctx.templates[first][1]['Arn']
    with pytest.raises(NoData, match='parent or SID'):
        access_entries_per_template(ctx)

    ctx = Context()
    first = ctx.connectors[0]['Arn']
    template_arn = ctx.templates[first][0]['Arn']
    ctx.entries[template_arn].append(dict(ctx.entries[template_arn][0], GroupDisplayName='x'))
    with pytest.raises(NoData, match='changed during pagination'):
        access_entries_per_template(ctx)


def test_pca_connector_ad_rejects_unresolved_parent_states():
    ctx = Context()
    ctx.connectors[0]['Status'] = 'DELETING'
    with pytest.raises(NoData, match='connector child inventory'):
        templates_per_connector(ctx)

    ctx = Context()
    first = ctx.connectors[0]['Arn']
    ctx.templates[first][0]['Status'] = 'DELETING'
    with pytest.raises(NoData, match='template child inventory'):
        access_entries_per_template(ctx)


def test_pca_connector_ad_checks_are_registered_with_read_permissions():
    assert {(SERVICE, code) for code, _, _ in CHECKS} <= custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('ListConnectors', 'ListTemplates',
                   'ListTemplateGroupAccessControlEntries'):
        assert f'"{SERVICE}:{action}"' in policy
