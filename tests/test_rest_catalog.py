from unittest.mock import Mock
from modules.qmchecks.codedeploy import CHECKS as CD
from modules.qmchecks.eks import CHECKS as EKS
from modules.qmchecks.redshift import CHECKS as RS
from modules.qmchecks.efs import CHECKS as EFS
from modules.qmchecks.mq import CHECKS as MQ

def test_rest_catalog_resource_counts():
    # CodeDeploy lists application names, the others list resource objects.
    c = Mock()
    c.call.side_effect = [['app'], [{'a': 1}], [{'NumberOfNodes': 2}],
                          [{'FileSystemId': 'fs-11111111'}], [{'a': 1}]]
    assert CD[0][2](c)['usage'] == 1
    assert EKS[0][2](c)['usage'] == 1
    assert RS[0][2](c)['usage'] == 2
    file_systems = next(check for check in EFS if check[0] == 'L-848C634D')
    assert file_systems[2](c)['usage'] == 1
    assert MQ[0][2](c)['usage'] == 1
