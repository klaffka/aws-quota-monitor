from unittest.mock import Mock

from modules.qmchecks.iotcore import CHECKS


def test_iotcore_persistent_resources_are_paginated():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'name': 'template'}],
        [{'roleAlias': 'alias'}],
        [{'authorizerName': 'one', 'status': 'ACTIVE'}, {'authorizerName': 'two', 'status': 'INACTIVE'}],
        [{'authorizerName': 'one', 'status': 'ACTIVE'}, {'authorizerName': 'two', 'status': 'INACTIVE'}],
        [{'ruleName': 'rule'}],
        [{'templateName': 'template-a'}, {'templateName': 'template-b'}],
        [{'versionId': '1'}, {'versionId': '2'}],
        [{'versionId': '1'}],
        [{'policyName': 'policy-a'}, {'policyName': 'policy-b'}],
        [{'versionId': '1'}, {'versionId': '2'}, {'versionId': '3'}],
        [{'versionId': '1'}],
    ]
    assert [check(ctx)['usage'] for _, _, check in CHECKS] == [1, 1, 2, 1, 1, 2, 3]
