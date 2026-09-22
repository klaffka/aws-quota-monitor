
import pytest

from modules.qmchecks.refactor_spaces import (
    CHECKS,
    applications,
    environments,
    routes,
    services,
)
from modules.qmcore.aws import NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants


class RefactorContext:
    account = '111111111111'

    def __init__(self):
        self.environment_items = [
            self.item('EnvironmentId', 'env-a', 'environment', self.account),
            self.item('EnvironmentId', 'env-b', 'environment', '222222222222'),
        ]
        self.application_items = {
            'env-a': [
                self.item('ApplicationId', 'app-a', 'application', self.account,
                          EnvironmentId='env-a'),
                self.item('ApplicationId', 'app-b', 'application', self.account,
                          EnvironmentId='env-a'),
            ],
            'env-b': [
                self.item('ApplicationId', 'app-c', 'application', '222222222222',
                          EnvironmentId='env-b'),
            ],
        }
        self.service_items = {
            ('env-a', 'app-a'): [
                self.item('ServiceId', 'svc-a', 'service', self.account,
                          EnvironmentId='env-a', ApplicationId='app-a'),
                self.item('ServiceId', 'svc-b', 'service', self.account,
                          EnvironmentId='env-a', ApplicationId='app-a'),
            ],
            ('env-a', 'app-b'): [
                self.item('ServiceId', 'svc-c', 'service', self.account,
                          EnvironmentId='env-a', ApplicationId='app-b'),
            ],
            ('env-b', 'app-c'): [
                self.item('ServiceId', 'svc-d', 'service', '222222222222',
                          EnvironmentId='env-b', ApplicationId='app-c'),
            ],
        }
        self.route_items = {
            ('env-a', 'app-a'): [
                self.item('RouteId', 'route-a', 'route', self.account,
                          EnvironmentId='env-a', ApplicationId='app-a'),
                self.item('RouteId', 'route-b', 'route', self.account,
                          EnvironmentId='env-a', ApplicationId='app-a', State='INACTIVE'),
            ],
            ('env-a', 'app-b'): [],
            ('env-b', 'app-c'): [
                self.item('RouteId', 'route-c', 'route', '222222222222',
                          EnvironmentId='env-b', ApplicationId='app-c'),
            ],
        }

    @staticmethod
    def item(id_field, identity, subject, owner, **values):
        state = values.pop('State', 'ACTIVE')
        return {id_field: identity, 'Arn': f'arn:refactor:{subject}:{identity}',
                'OwnerAccountId': owner, 'State': state, **values}

    def call(self, service, method, key=None, **kwargs):
        assert service == 'migration-hub-refactor-spaces'
        if method == 'list_environments':
            return self.environment_items
        environment = kwargs['EnvironmentIdentifier']
        if method == 'list_applications':
            return self.application_items[environment]
        application = kwargs['ApplicationIdentifier']
        if method == 'list_services':
            return self.service_items[(environment, application)]
        if method == 'list_routes':
            return self.route_items[(environment, application)]
        raise AssertionError((method, key, kwargs))


def test_refactor_spaces_counts_owned_resources_across_visible_hierarchies():
    ctx = RefactorContext()
    assert [check(ctx)['usage'] for _, _, check in CHECKS] == [1, 2, 3, 2]


def test_refactor_spaces_inventories_preserve_complete_parent_tree():
    ctx = RefactorContext()
    assert len(environments(ctx)) == 2
    assert len(applications(ctx)) == 3
    assert len(services(ctx)) == 4
    assert len(routes(ctx)) == 3


def test_refactor_spaces_rejects_duplicate_and_mismatched_resources():
    ctx = RefactorContext()
    ctx.application_items['env-a'].append(dict(ctx.application_items['env-a'][0]))
    with pytest.raises(NoData, match='contains a duplicate'):
        applications(ctx)

    ctx = RefactorContext()
    ctx.service_items[('env-a', 'app-a')][0]['ApplicationId'] = 'app-b'
    with pytest.raises(NoData, match='inconsistent parent'):
        services(ctx)


def test_refactor_spaces_rejects_unknown_state_or_missing_owner():
    ctx = RefactorContext()
    ctx.environment_items[0]['State'] = 'FUTURE_STATE'
    with pytest.raises(NoData, match='missing required identity data'):
        environments(ctx)

    ctx = RefactorContext()
    del ctx.route_items[('env-a', 'app-a')][0]['OwnerAccountId']
    with pytest.raises(NoData, match='missing required identity data'):
        routes(ctx)


def test_refactor_spaces_is_registered_with_read_permissions():
    assert {('refactor-spaces', code) for code, _, _ in CHECKS} <= custom_keys()
    for action in ('ListEnvironments', 'ListApplications', 'ListServices', 'ListRoutes'):
        assert grants(f'refactor-spaces:{action}')
