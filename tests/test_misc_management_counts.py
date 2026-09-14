from unittest.mock import Mock

from modules.qmchecks.wellarchitected import CHECKS as WA
from modules.qmchecks.ssm_contacts import CHECKS as CONTACTS
from modules.qmchecks.dataexchange import CHECKS as DATASETS
from modules.qmchecks.rbin import CHECKS as RBIN


def test_misc_management_resource_counts():
    for checks in (WA, CONTACTS):
        context = Mock(); context.call.side_effect = [[{}]] * len(checks)
        assert [check[2](context)['usage'] for check in checks] == [1] * len(checks)
    for checks in (DATASETS,):
        context = Mock(); context.call.return_value = [{}]
        assert checks[0][2](context)['usage'] == 1
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
