import json
from pathlib import Path

from modules.qmchecks.aoss import (CHECKS, allocated_capacity, collections_per_group,
                                   document_bytes, policy_size, security_config_size)


class Context:
    def __init__(self, responses):
        self.responses = responses

    def call(self, service, method, key=None, **kwargs):
        value = self.responses[(method, json.dumps(kwargs, sort_keys=True))]
        return value[key] if key else value


def k(method, **kwargs):
    return method, json.dumps(kwargs, sort_keys=True)


def test_policy_size_uses_compact_utf8_wire_document():
    ctx = Context({
        k('list_security_policies', type='network'): {
            'securityPolicySummaries': [{'name': 'net-one'}]},
        k('get_security_policy', type='network', name='net-one'): {
            'securityPolicyDetail': {'name': 'net-one', 'type': 'network',
                                     'policy': [{'Description': 'Grüße'}]}},
    })
    expected = len('[{"Description":"Grüße"}]'.encode('utf-8'))
    assert document_bytes([{'Description': 'Grüße'}]) == expected
    assert policy_size(ctx, 'network')['usage'] == expected


def test_saml_size_counts_metadata_bytes_only():
    ctx = Context({
        k('list_security_configs', type='saml'): {
            'securityConfigSummaries': [{'id': 'cfg-1'}]},
        k('get_security_config', id='cfg-1'): {
            'securityConfigDetail': {'id': 'cfg-1', 'type': 'saml',
                                     'samlOptions': {'metadata': 'ä'}}},
    })
    assert security_config_size(ctx, 'saml')['usage'] == 2


def test_collection_generation_and_allocated_capacity_are_scoped_correctly():
    groups = [
        {'name': 'classic', 'generation': 'CLASSIC', 'numberOfCollections': 3,
         'capacityLimits': {'maxIndexingCapacityInOCU': 16, 'maxSearchCapacityInOCU': 8}},
        {'name': 'next', 'generation': 'NEXTGEN', 'numberOfCollections': 7,
         'capacityLimits': {'maxIndexingCapacityInOCU': 32, 'maxSearchCapacityInOCU': 16}},
        {'name': 'empty', 'generation': 'NEXTGEN', 'numberOfCollections': 0,
         'capacityLimits': {'maxIndexingCapacityInOCU': 96, 'maxSearchCapacityInOCU': 96}},
    ]
    ctx = Context({
        k('list_collection_groups'): {'collectionGroupSummaries': groups},
        k('get_account_settings'): {'accountSettingsDetail': {'capacityLimits': {
            'maxIndexingCapacityInOCU': 10, 'maxSearchCapacityInOCU': 12}}},
    })
    assert collections_per_group(ctx, 'CLASSIC')['usage'] == 3
    assert collections_per_group(ctx, 'NEXTGEN')['usage'] == 7
    assert allocated_capacity(ctx, 'maxIndexingCapacityInOCU')['usage'] == 58


def test_aoss_registers_every_catalog_quota():
    catalog = json.loads(open('tests/fixtures/selected-service-quotas.json',
                              encoding='utf-8').read())
    expected = {q['QuotaCode'] for q in catalog if q['ServiceCode'] == 'aoss'}
    assert {code for code, _name, _fn in CHECKS} == expected


def test_aoss_read_permissions_are_deployed():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    for action in ('GetSecurityConfig', 'GetSecurityPolicy', 'GetAccessPolicy',
                   'ListLifecyclePolicies', 'BatchGetLifecyclePolicy',
                   'ListCollectionGroups', 'GetAccountSettings'):
        assert f'"opensearchserverless:{action}"' in policy
