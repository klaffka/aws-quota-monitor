from pathlib import Path

import pytest

from modules.qmchecks.misc_counts import dlm_share_targets
from modules.qmcore.aws import NoData


class DLMContext:
    def __init__(self):
        self.policies = [{'PolicyId': 'policy-b'}, {'PolicyId': 'policy-a'}]
        self.details = {
            'policy-a': {'Policy': {'PolicyId': 'policy-a', 'PolicyDetails': {
                'Schedules': [{'ShareRules': [
                    {'TargetAccounts': ['111111111111', '222222222222']},
                    {'TargetAccounts': ['333333333333']},
                ]}],
            }}},
            'policy-b': {'Policy': {'PolicyId': 'policy-b', 'PolicyDetails': {
                'Schedules': [{}, {'ShareRules': [
                    {'TargetAccounts': ['444444444444', '555555555555', '666666666666']},
                ]}],
            }}},
        }

    def call(self, service, method, key=None, **kwargs):
        assert service == 'dlm'
        if method == 'get_lifecycle_policies':
            return self.policies
        if method == 'get_lifecycle_policy':
            return self.details[kwargs['PolicyId']]
        raise AssertionError(method)


def test_dlm_target_accounts_uses_maximum_single_sharing_rule():
    result = dlm_share_targets(DLMContext())
    assert (result['usage'], result['resource_id']) == (3, 'policy-b/1/0')
    assert result['meta'] is None


def test_dlm_target_accounts_rejects_duplicate_accounts_and_inconsistent_details():
    ctx = DLMContext()
    rule = ctx.details['policy-a']['Policy']['PolicyDetails']['Schedules'][0]['ShareRules'][0]
    rule['TargetAccounts'].append('111111111111')
    with pytest.raises(NoData, match='invalid target accounts'):
        dlm_share_targets(ctx)

    ctx = DLMContext()
    ctx.details['policy-a']['Policy']['PolicyId'] = 'policy-other'
    with pytest.raises(NoData, match='detail is inconsistent'):
        dlm_share_targets(ctx)


def test_dlm_configuration_check_has_read_permission():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"dlm:GetLifecyclePolicy"' in policy
