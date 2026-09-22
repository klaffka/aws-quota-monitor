
import pytest

from modules.qmchecks.proton import (
    component_count,
    connections_per_environment_account,
    service_instances_per_service,
    template_count,
    template_versions_per_template,
)
from modules.qmcore.aws import NoData
from tests.iam_policy import grants


class ProtonContext:
    account = '111111111111'

    def __init__(self):
        self.calls = []
        self.responses = {
            ('list_environment_templates', ()): [
                {'arn': 'arn:environment-template:env-one', 'name': 'env-one'},
            ],
            ('list_service_templates', ()): [
                {'arn': 'arn:service-template:svc-one', 'name': 'svc-one'},
            ],
            ('list_components', ()): [
                {'arn': 'arn:component:one', 'name': 'one'},
                {'arn': 'arn:component:two', 'name': 'two'},
            ],
            ('list_environment_account_connections', (('requestedBy', 'MANAGEMENT_ACCOUNT'),)): [
                {'id': 'connection-one', 'environmentAccountId': '222222222222',
                 'managementAccountId': self.account},
                {'id': 'connection-two', 'environmentAccountId': '222222222222',
                 'managementAccountId': self.account},
                {'id': 'connection-three', 'environmentAccountId': '333333333333',
                 'managementAccountId': self.account},
            ],
            ('list_environment_account_connections', (('requestedBy', 'ENVIRONMENT_ACCOUNT'),)): [],
            ('list_environment_template_versions', (('templateName', 'env-one'),)): [
                {'arn': 'arn:env:1.1', 'templateName': 'env-one',
                 'majorVersion': '1', 'minorVersion': '1'},
            ],
            ('list_environment_template_versions',
             (('majorVersion', '1'), ('templateName', 'env-one'))): [
                {'arn': 'arn:env:1.0', 'templateName': 'env-one',
                 'majorVersion': '1', 'minorVersion': '0'},
                {'arn': 'arn:env:1.1', 'templateName': 'env-one',
                 'majorVersion': '1', 'minorVersion': '1'},
            ],
            ('list_service_template_versions', (('templateName', 'svc-one'),)): [
                {'arn': 'arn:svc:1.0', 'templateName': 'svc-one',
                 'majorVersion': '1', 'minorVersion': '0'},
                {'arn': 'arn:svc:2.0', 'templateName': 'svc-one',
                 'majorVersion': '2', 'minorVersion': '0'},
            ],
            ('list_service_template_versions',
             (('majorVersion', '1'), ('templateName', 'svc-one'))): [
                {'arn': 'arn:svc:1.0', 'templateName': 'svc-one',
                 'majorVersion': '1', 'minorVersion': '0'},
                {'arn': 'arn:svc:1.1', 'templateName': 'svc-one',
                 'majorVersion': '1', 'minorVersion': '1'},
                {'arn': 'arn:svc:1.2', 'templateName': 'svc-one',
                 'majorVersion': '1', 'minorVersion': '2'},
            ],
            ('list_service_template_versions',
             (('majorVersion', '2'), ('templateName', 'svc-one'))): [
                {'arn': 'arn:svc:2.0', 'templateName': 'svc-one',
                 'majorVersion': '2', 'minorVersion': '0'},
            ],
            ('list_service_instances', ()): [
                {'arn': 'arn:instance:one', 'name': 'one', 'serviceName': 'service-a'},
                {'arn': 'arn:instance:two', 'name': 'two', 'serviceName': 'service-a'},
                {'arn': 'arn:instance:three', 'name': 'one', 'serviceName': 'service-b'},
            ],
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'proton'
        self.calls.append((method, kwargs))
        return self.responses[(method, tuple(sorted(kwargs.items())))]


def test_proton_account_counts_include_both_template_types_and_components():
    ctx = ProtonContext()
    assert template_count(ctx)['usage'] == 2
    assert component_count(ctx)['usage'] == 2


def test_proton_connections_use_maximum_per_environment_account_and_both_views():
    ctx = ProtonContext()
    result = connections_per_environment_account(ctx)
    assert (result['usage'], result['resource_id']) == (2, '222222222222')
    assert result['meta'] is None
    assert [kwargs['requestedBy'] for method, kwargs in ctx.calls
            if method == 'list_environment_account_connections'] == [
                'MANAGEMENT_ACCOUNT', 'ENVIRONMENT_ACCOUNT']


def test_proton_template_versions_include_every_minor_version_of_both_types():
    result = template_versions_per_template(ProtonContext())
    assert (result['usage'], result['resource_id']) == (4, 'service:svc-one')
    assert result['meta'] is None


def test_proton_service_instances_use_maximum_per_service():
    result = service_instances_per_service(ProtonContext())
    assert (result['usage'], result['resource_id']) == (2, 'service-a')
    assert result['meta'] is None


def test_proton_rejects_duplicate_and_inconsistent_inventories():
    ctx = ProtonContext()
    ctx.responses[('list_components', ())].append(
        dict(ctx.responses[('list_components', ())][0]))
    with pytest.raises(NoData, match='contains a duplicate'):
        component_count(ctx)

    ctx = ProtonContext()
    key = ('list_service_template_versions',
           (('majorVersion', '1'), ('templateName', 'svc-one')))
    ctx.responses[key][0]['templateName'] = 'other'
    with pytest.raises(NoData, match='inconsistent parent'):
        template_versions_per_template(ctx)

    ctx = ProtonContext()
    key = ('list_environment_account_connections',
           (('requestedBy', 'MANAGEMENT_ACCOUNT'),))
    ctx.responses[key][0]['managementAccountId'] = '999999999999'
    with pytest.raises(NoData, match='inconsistent account scope'):
        connections_per_environment_account(ctx)


def test_proton_configuration_has_all_read_permissions():
    for action in (
        'ListEnvironmentTemplates', 'ListEnvironmentAccountConnections',
        'ListComponents', 'ListEnvironmentTemplateVersions',
        'ListServiceTemplateVersions', 'ListServiceInstances',
    ):
        assert grants(f'proton:{action}')
