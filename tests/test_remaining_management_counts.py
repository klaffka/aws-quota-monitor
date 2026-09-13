from unittest.mock import Mock

from modules.qmchecks.discovery import CHECKS as DISCOVERY
from modules.qmchecks.ssm_incidents import CHECKS as INCIDENTS
from modules.qmchecks.workspaces_instances import CHECKS as INSTANCES
from modules.qmchecks.repostspace import CHECKS as REPOST
from modules.qmchecks.evidently import CHECKS as EVIDENTLY


def test_remaining_management_resource_counts():
    for checks in (DISCOVERY, INCIDENTS, INSTANCES, REPOST, EVIDENTLY):
        context = Mock(); context.call.return_value = [{}]
        assert checks[0][2](context)['usage'] == 1
