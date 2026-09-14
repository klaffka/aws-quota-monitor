from unittest.mock import Mock

from modules.qmchecks.dsql import CHECKS as DSQL
from modules.qmchecks.payment_cryptography import CHECKS as PAYMENT
from modules.qmchecks.serverlessrepo import CHECKS as SERVERLESS
from modules.qmchecks.swf import CHECKS as SWF
from modules.qmchecks.cloudhsm import CHECKS as CLOUDHSM


def test_final_catalog_resource_counts():
    for checks in (DSQL, PAYMENT, SERVERLESS, CLOUDHSM):
        context = Mock()
        context.call.return_value = [{}]
        assert checks[0][2](context)['usage'] == 1
    context = Mock()
    context.call.return_value = [{}]
    assert SWF[0][2](context)['usage'] == 1
    assert context.call.call_args.kwargs['registrationStatus'] == 'REGISTERED'
