from unittest.mock import Mock
from modules.qmchecks.codedeploy import CHECKS as CD
from modules.qmchecks.eks import CHECKS as EKS
from modules.qmchecks.redshift import CHECKS as RS
from modules.qmchecks.efs import CHECKS as EFS
from modules.qmchecks.mq import CHECKS as MQ

def test_rest_catalog_resource_counts():
 c=Mock(); c.call.side_effect=[[{'a':1}],[{'a':1}],[{'NumberOfNodes':2}],[{'a':1}],[{'a':1}]]
 assert CD[0][2](c)['usage']==1; assert EKS[0][2](c)['usage']==1; assert RS[0][2](c)['usage']==2; assert EFS[0][2](c)['usage']==1; assert MQ[0][2](c)['usage']==1
