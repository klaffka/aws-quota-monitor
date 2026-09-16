from unittest.mock import Mock

from modules.qmchecks.sagemaker_instances import CHECKS as INSTANCE_CHECKS
from modules.qmchecks.sagemaker_resources import ALL_CHECKS
from modules.qmchecks.bedrock import CHECKS as BEDROCK

# The instance-type checks read a job's configuration rather than counting a
# listing, so they are exercised against stubbed responses in their own test.
LIST_CHECKS = [check for check in ALL_CHECKS[4:len(ALL_CHECKS) - len(INSTANCE_CHECKS)]
               if check[0] != 'L-7A3DF611']


def test_sagemaker_and_bedrock_resource_extensions():
    context = Mock()
    context.call.side_effect = [[{}]] * len(LIST_CHECKS)
    assert [check(context)['usage'] for _code, _name, check in LIST_CHECKS] == [1] * len(LIST_CHECKS)
    context = Mock()
    account_checks = {'L-97D79C54', 'L-D321719B', 'L-CB5B847D', 'L-0E5A840C',
                      'L-45B04988', 'L-40EC9882', 'L-B783C50B', 'L-23CF4444'}
    context.call.side_effect = [[{'blueprintArn': 'arn:blueprint'}]] * len(account_checks)
    selected = [check for check in BEDROCK if check[0] in account_checks]
    assert [check[2](context)['usage'] for check in selected] == [1] * len(selected)
