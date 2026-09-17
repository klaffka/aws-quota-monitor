from unittest.mock import Mock

from modules.qmchecks.wellarchitected import CHECKS as WA
from modules.qmchecks.ssm_contacts import CHECKS as CONTACTS
from modules.qmchecks.dataexchange import CHECKS as DATASETS
from modules.qmchecks.rbin import CHECKS as RBIN


# The plan- and rotation-scoped contact checks descend into a contact; they are
# covered by tests/test_ssm_contacts_plans.py against a real client. The
# Well-Architected share checks descend into a lens, workload or review template
# and are covered by tests/test_databrew_and_wellarchitected_scopes.py.
SCOPED = {'L-5AE11799', 'L-F338226A', 'L-D438A616',
          'L-E62A1DE4', 'L-7E98904D', 'L-A5DDC022'}


def test_misc_management_resource_counts():
    for checks in (WA, CONTACTS):
        flat = [check for check in checks if check[0] not in SCOPED]
        context = Mock(); context.call.side_effect = [[{}]] * len(flat)
        assert [check[2](context)['usage'] for check in flat] == [1] * len(flat)
    # Data sets carry an identity and an asset type; see tests/test_dataexchange.py.
    context = Mock()
    context.call.return_value = [{'Id': 'set-1', 'AssetType': 'S3_SNAPSHOT'}]
    assert DATASETS[0][2](context)['usage'] == 1
    context = Mock()
    context.call.side_effect = [
        [{'Identifier': 'RULE0000001'}],
        [],
        [],
        [{'Identifier': 'RULE0000001'}],
        [],
        [],
        {'Identifier': 'RULE0000001', 'ResourceType': 'EBS_SNAPSHOT',
         'ResourceTags': []},
    ]
    assert [check[2](context)['usage'] for check in RBIN] == [1, 0]
