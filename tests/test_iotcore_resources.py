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
    # The original seven checks, in order; the endpoint, rule and thing group
    # checks added later have their own tests.
    original = ['L-345B62A1', 'L-8AF17D80', 'L-78E3C43F', 'L-FC25158E',
                'L-954FA751', 'L-71FA7EC4', 'L-5F6C2444']
    by_code = {code: check for code, _, check in CHECKS}
    assert [by_code[code](ctx)['usage'] for code in original] == [1, 1, 2, 1, 1, 2, 3]
