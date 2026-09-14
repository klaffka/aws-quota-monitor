from pathlib import Path

import pytest

from modules.qmchecks.pca_connector_scep import (
    CHECKS,
    challenges_per_connector,
    connector_count,
    connectors,
)
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys


ACCOUNT = '111111111111'
REGION = 'eu-central-1'
SERVICE = 'pca-connector-scep'


def connector(identity, **values):
    return {'Arn': f'arn:aws:{SERVICE}:{REGION}:{ACCOUNT}:connector/{identity}',
            'Status': 'ACTIVE', **values}


def challenge(connector_arn, identity, **values):
    return {'Arn': f'{connector_arn}/challenge/{identity}',
            'ConnectorArn': connector_arn, **values}


class Context:
    account = ACCOUNT
    region = REGION

    def __init__(self):
        self.connectors = [connector('connector-one'), connector('connector-two')]
        first, second = (item['Arn'] for item in self.connectors)
        self.challenges = {
            first: [challenge(first, 'challenge-one'),
                    challenge(first, 'challenge-two')],
            second: [challenge(second, 'challenge-three')],
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == SERVICE
        if method == 'list_connectors':
            return self.connectors
        if method == 'list_challenge_metadata':
            return self.challenges[kwargs['ConnectorArn']]
        raise AssertionError((method, key, kwargs))


def test_pca_connector_scep_counts_both_resource_scopes():
    ctx = Context()
    assert connector_count(ctx)['usage'] == 2
    result = challenges_per_connector(ctx)
    assert (result['usage'], result['resource_id']) == (2, ctx.connectors[0]['Arn'])


def test_pca_connector_scep_deduplicates_identical_repeated_pages():
    ctx = Context()
    ctx.connectors.append(dict(ctx.connectors[0]))
    first = ctx.connectors[0]['Arn']
    ctx.challenges[first].append(dict(ctx.challenges[first][0]))
    assert len(connectors(ctx)) == 2
    assert challenges_per_connector(ctx)['usage'] == 2


def test_pca_connector_scep_rejects_invalid_connector_identity_or_state():
    ctx = Context()
    ctx.connectors[0]['Arn'] = ctx.connectors[0]['Arn'].replace(REGION, 'eu-west-1')
    with pytest.raises(NoData, match='inconsistent ARN'):
        connectors(ctx)

    ctx = Context()
    ctx.connectors[0]['Status'] = 'FUTURE'
    with pytest.raises(NoData, match='unknown state'):
        connectors(ctx)


def test_pca_connector_scep_rejects_invalid_challenge_parent_or_conflict():
    ctx = Context()
    first = ctx.connectors[0]['Arn']
    ctx.challenges[first][0]['ConnectorArn'] = ctx.connectors[1]['Arn']
    with pytest.raises(NoData, match='inconsistent parent'):
        challenges_per_connector(ctx)

    ctx = Context()
    first = ctx.connectors[0]['Arn']
    ctx.challenges[first].append(dict(ctx.challenges[first][0], UpdatedAt='changed'))
    with pytest.raises(NoData, match='changed during pagination'):
        challenges_per_connector(ctx)


def test_pca_connector_scep_rejects_unresolved_connector_state():
    ctx = Context()
    ctx.connectors[0]['Status'] = 'DELETING'
    with pytest.raises(NoData, match='child inventory'):
        challenges_per_connector(ctx)


def test_pca_connector_scep_checks_are_registered_with_read_permissions():
    assert {(SERVICE, code) for code, _, _ in CHECKS} <= custom_keys()
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('ListConnectors', 'ListChallengeMetadata'):
        assert f'"{SERVICE}:{action}"' in policy
