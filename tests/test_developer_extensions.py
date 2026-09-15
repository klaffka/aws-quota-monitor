from unittest.mock import Mock
from modules.qmchecks.amplify import CHECKS as AMPLIFY
from modules.qmchecks.servicecatalog import CHECKS as CATALOG


def test_developer_resource_extensions():
    context = Mock(); context.call.side_effect = [[{'appId': 'a'}], [{}]]
    assert AMPLIFY[1][2](context)['usage'] == 1
    context = Mock(); context.call.return_value = [{}]
    service_actions = next(check for code, _, check in CATALOG
                           if code == 'L-BEE0DD19')
    assert service_actions(context)['usage'] == 1
