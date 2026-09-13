from pathlib import Path
from unittest.mock import Mock

import pytest

from modules.qmchecks.auditmanager import CHECKS, accounts_in_scope, controls_per_framework
from modules.qmcore.aws import NoData


def test_auditmanager_counts_custom_resources_and_running_assessments():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert CHECKS[0][2](ctx)['usage'] == 2
    assert CHECKS[1][2](ctx)['usage'] == 2
    assert CHECKS[2][2](ctx)['usage'] == 2


def test_auditmanager_controls_use_maximum_per_framework():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'framework-1'}, {'id': 'framework-2'}],
        {'framework': {'controlSets': [{'controls': [{'id': 'a'}]}]}},
        {'framework': {'controlSets': [{'controls': [{'id': 'a'}, {'id': 'b'}]}]}},
    ]
    result = controls_per_framework(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'framework-2')


def test_auditmanager_accounts_in_scope_counts_unique_accounts_across_assessments():
    class Context:
        def call(self, service, method, key=None, **kwargs):
            assert service == 'auditmanager'
            if method == 'list_assessments':
                return [{'id': 'assessment-b'}, {'id': 'assessment-a'}]
            accounts = {
                'assessment-a': ['111111111111', '222222222222'],
                'assessment-b': ['222222222222', '333333333333'],
            }[kwargs['assessmentId']]
            return {'assessment': {'metadata': {
                'id': kwargs['assessmentId'],
                'scope': {'awsAccounts': [{'id': account} for account in accounts]},
            }}}

    result = accounts_in_scope(Context())
    assert result['usage'] == 3
    assert result['method'] == 'ACCOUNT_COUNT'
    assert 'meta' not in result


def test_auditmanager_accounts_in_scope_rejects_incomplete_details_and_has_permission():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'id': 'assessment-a'}],
        {'assessment': {'metadata': {'id': 'assessment-a'}}},
    ]
    with pytest.raises(NoData, match='invalid account scope'):
        accounts_in_scope(ctx)

    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"auditmanager:GetAssessment"' in policy
