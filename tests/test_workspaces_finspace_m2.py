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
                            [{'environmentId': 'env'}]]
    assert [check[2](ctx)['usage'] for check in WORKSPACES] == [1] * len(WORKSPACES)
    assert FINSPACE[0][2](ctx)['usage'] == 1


def test_m2_inventories_and_environment_storage():
    """The storage scopes describe each environment, so answer by method."""
    ctx = Mock()

    def calls(service, method, key=None, **kwargs):
        if method == 'list_applications':
            return [{'applicationId': 'app'}]
        if method == 'list_environments':
            return [{'environmentId': 'quiet'}, {'environmentId': 'busy'}]
        if method == 'get_environment':
            mounts = {'quiet': [{'efs': {}}],
                      'busy': [{'efs': {}}, {'efs': {}}, {'fsx': {}}]}
            return {'storageConfigurations': mounts[kwargs['environmentId']]}
        raise AssertionError(f'unexpected call: {method}')

    ctx.call.side_effect = calls
    usage = {code: check(ctx)['usage'] for code, _name, check in M2}
    assert (usage['L-00464274'], usage['L-6851C542']) == (1, 2)
    # The busier environment mounts two EFS filesystems and one FSx.
    assert (usage['L-5D943D0B'], usage['L-C1C41257']) == (2, 1)
