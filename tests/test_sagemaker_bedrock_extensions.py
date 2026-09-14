from unittest.mock import Mock

from modules.qmchecks.sagemaker_resources import ALL_CHECKS
from modules.qmchecks.bedrock import CHECKS as BEDROCK


def test_sagemaker_and_bedrock_resource_extensions():
    context = Mock()
    context.call.side_effect = [[{}]] * (len(ALL_CHECKS) - 4)
    assert [check(context)['usage'] for code, _, check in ALL_CHECKS[4:] if code != 'L-7A3DF611'] == [1] * (len(ALL_CHECKS) - 5)
    context = Mock()
    account_checks = {'L-97D79C54', 'L-D321719B', 'L-CB5B847D', 'L-0E5A840C',
                      'L-45B04988', 'L-40EC9882', 'L-B783C50B', 'L-23CF4444'}
    context.call.side_effect = [[{'blueprintArn': 'arn:blueprint'}]] * len(account_checks)
    selected = [check for check in BEDROCK if check[0] in account_checks]
    assert [check[2](context)['usage'] for check in selected] == [1] * len(selected)
