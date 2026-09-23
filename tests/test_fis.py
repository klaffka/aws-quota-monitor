import json
from pathlib import Path

import pytest

from modules.qmchecks.fis import (
    CHECKS,
    TARGET_CHECKS,
    experiment_templates,
    parallel_actions,
    resolved_target_usage,
    target_accounts_per_template,
    template_maximum,
)
from modules.qmcore.aws import NoData
from tests.iam_policy import grants


class Context:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def call(self, service, method, key=None, **kwargs):
        self.calls.append((service, method, key, kwargs))
        lookup = (method, json.dumps(kwargs, sort_keys=True))
        value = self.responses[lookup]
        if key:
            return value[key]
        return value


def key(method, **kwargs):
    return method, json.dumps(kwargs, sort_keys=True)


def template_responses():
    return {
        key('list_experiment_templates'): {
            'experimentTemplates': [{'id': 't-2'}, {'id': 't-1'}],
        },
        key('get_experiment_template', id='t-1'): {
            'experimentTemplate': {
                'id': 't-1', 'actions': {'a': {}}, 'stopConditions': [], 'targets': {},
                'targetAccountConfigurationsCount': 2,
            },
        },
        key('get_experiment_template', id='t-2'): {
            'experimentTemplate': {
                'id': 't-2', 'actions': {'a': {}, 'b': {}, 'c': {}},
                'stopConditions': [{}, {}], 'targets': {},
                'targetAccountConfigurationsCount': 1,
            },
        },
    }


def experiment(status='running', *, multi_account=False):
    return {
        'id': 'exp-1',
        'state': {'status': status},
        'targetAccountConfigurationsCount': 1 if multi_account else 0,
        'targets': {
            'dynamic': {
                'resourceType': 'aws:ec2:instance',
                'resourceTags': {'environment': 'test'},
                'parameters': {},
            },
            'explicit': {
                'resourceType': 'aws:ec2:instance',
                'resourceArns': ['arn:aws:ec2:eu-central-1:123456789012:instance/i-3'],
                'resourceTags': {},
                'parameters': {},
            },
        },
        'actions': {
            'stop': {
                'actionId': 'aws:ec2:stop-instances',
                'targets': {'Instances': 'dynamic'},
                'state': {'status': 'running'},
            },
            'stop-explicit': {
                'actionId': 'aws:ec2:stop-instances',
                'targets': {'Instances': 'explicit'},
                'state': {'status': 'pending'},
            },
            'wait': {
                'actionId': 'aws:fis:wait',
                'targets': {},
                'state': {'status': 'stopping'},
            },
            'done': {
                'actionId': 'aws:fis:wait',
                'targets': {},
                'state': {'status': 'completed'},
            },
        },
    }


def experiment_responses(status='running', *, multi_account=False):
    detail = experiment(status, multi_account=multi_account)
    return {
        key('list_experiments'): {
            'experiments': [
                {'id': 'old', 'state': {'status': 'completed'}},
                {'id': 'exp-1', 'state': {'status': status}},
            ],
        },
        key('get_experiment', id='exp-1'): {'experiment': detail},
        key('list_experiment_resolved_targets', experimentId='exp-1'): {
            'resolvedTargets': [
                {'resourceType': 'aws:ec2:instance', 'targetName': 'dynamic',
                 'targetInformation': {'resourceArn': 'arn:aws:ec2:::instance/i-1'}},
                {'resourceType': 'aws:ec2:instance', 'targetName': 'dynamic',
                 'targetInformation': {'resourceArn': 'arn:aws:ec2:::instance/i-2'}},
                # A repeated page item must not inflate the quota.
                {'resourceType': 'aws:ec2:instance', 'targetName': 'dynamic',
                 'targetInformation': {'resourceArn': 'arn:aws:ec2:::instance/i-2'}},
                {'resourceType': 'aws:ec2:instance', 'targetName': 'explicit',
                 'targetInformation': {'resourceArn': 'arn:aws:ec2:::instance/i-3'}},
            ],
        },
    }


def test_template_checks_use_complete_template_details_and_maximum():
    ctx = Context(template_responses())

    templates = experiment_templates(ctx)
    assert [item['id'] for item in templates] == ['t-1', 't-2']
    assert template_maximum(ctx, 'actions', 'FisExperimentTemplate')['usage'] == 3
    assert template_maximum(ctx, 'stopConditions', 'FisExperimentTemplate')['usage'] == 2
    assert target_accounts_per_template(ctx)['usage'] == 2


def test_resolved_target_quota_counts_unique_dynamic_targets_only():
    ctx = Context(experiment_responses())

    result = resolved_target_usage(ctx, 'aws:ec2:stop-instances', True)

    assert result['usage'] == 2
    assert result['resource_id'] == 'exp-1'
    assert result['method'] == 'PER_RESOURCE_MAX'


def test_target_quota_that_applies_to_all_selection_modes_includes_explicit_targets():
    ctx = Context(experiment_responses())

    result = resolved_target_usage(ctx, 'aws:ec2:stop-instances', False)

    assert result['usage'] == 3


def test_pending_target_resolution_and_multi_account_inventory_are_not_under_counted():
    with pytest.raises(NoData, match='resolution has not finished'):
        resolved_target_usage(Context(experiment_responses('initiating')),
                              'aws:ec2:stop-instances', True)
    with pytest.raises(NoData, match='target-account identity'):
        resolved_target_usage(Context(experiment_responses(multi_account=True)),
                              'aws:ec2:stop-instances', True)


def test_parallel_actions_count_only_currently_active_action_states():
    result = parallel_actions(Context(experiment_responses()))

    assert result['usage'] == 2
    assert result['resource_id'] == 'exp-1'


def test_fis_check_codes_match_catalog_and_target_actions_are_unique():
    catalog = json.loads(Path('tests/fixtures/selected-service-quotas.json')
                         .read_text(encoding='utf-8'))
    quotas = catalog['Quotas'] if isinstance(catalog, dict) else catalog
    fis_codes = {item['QuotaCode'] for item in quotas if item['ServiceCode'] == 'fis'}
    codes = [code for code, _name, _fn in CHECKS]

    assert len(codes) == len(set(codes))
    assert set(codes) <= fis_codes
    assert len(TARGET_CHECKS) == 40
    assert next(action for code, _name, action, _dynamic in TARGET_CHECKS
                if code == 'L-143DCE03') == 'aws:directconnect:virtual-interface-disconnect'


def test_fis_read_permissions_are_deployed():
    for action in ('ListExperimentTemplates', 'GetExperimentTemplate', 'ListExperiments',
                   'GetExperiment', 'ListExperimentResolvedTargets'):
        assert grants(f'fis:{action}')
