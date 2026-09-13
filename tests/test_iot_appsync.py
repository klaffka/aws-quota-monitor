from unittest.mock import Mock

from modules.qmchecks.iot import CHECKS as IOT
from modules.qmchecks.appsync import CHECKS as APPSYNC


def test_iot_dynamic_groups_and_appsync_graphql_apis():
    ctx = Mock()
    ctx.call.side_effect = [[{'groupName': 'dynamic'}], [{'apiId': 'api'}]]
    assert IOT[0][2](ctx)['usage'] == 1
    assert APPSYNC[0][2](ctx)['usage'] == 1
