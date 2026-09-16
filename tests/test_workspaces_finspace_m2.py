from unittest.mock import Mock

from modules.qmchecks.workspaces import CHECKS as WORKSPACES
from modules.qmchecks.finspace import CHECKS as FINSPACE
from modules.qmchecks.m2 import CHECKS as M2


def test_workspaces_finspace_and_m2_inventories():
    ctx = Mock()
    ctx.call.side_effect = [[{'Id': 'image'}], [{'Id': 'bundle'}], [{'WorkspaceId': 'ws'}],
                            [{'DirectoryId': 'directory'}], [{'DirectoryId': 'directory', 'IpGroupIds': ['group']}],
                            [{'DirectoryId': 'directory', 'IpGroupIds': ['group']}],
                            [{'GroupId': 'group', 'UserRules': ['rule']}], [{'Id': 'alias'}],
                            [{'environmentId': 'env'}], [{'applicationId': 'app'}],
                            [{'environmentId': 'm2env'}], [{'environmentId': 'm2env2'}]]
    assert [check[2](ctx)['usage'] for check in WORKSPACES] == [1] * len(WORKSPACES)
    assert FINSPACE[0][2](ctx)['usage'] == 1
    assert [check[2](ctx)['usage'] for check in M2] == [1, 1]
