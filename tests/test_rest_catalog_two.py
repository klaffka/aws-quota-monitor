from unittest.mock import Mock
from modules.qmchecks.cassandra import CHECKS as CASS
from modules.qmchecks.qldb import CHECKS as QLDB
from modules.qmchecks.cloud9 import CHECKS as C9
from modules.qmchecks.resource_explorer import CHECKS as RE
from modules.qmchecks.neptune_graph import CHECKS as NG
def test_rest_catalog_two_counts():
 c=Mock(); c.call.side_effect=[[{}],[{}],[{}],[{}],[{}],[{}]]
 assert [x[2](c)['usage'] for x in CASS]==[1,1]; assert QLDB[0][2](c)['usage']==1; assert C9[0][2](c)['usage']==1; assert RE[0][2](c)['usage']==1; assert NG[0][2](c)['usage']==1
