from unittest.mock import Mock

from modules.qmchecks.personalize import CHECKS as PERSONALIZE_CHECKS
from modules.qmchecks.sagemaker_resources import CHECKS as SAGEMAKER_CHECKS


def test_personalize_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}],
                            [{'datasetGroupArn': 'g1'}, {'datasetGroupArn': 'g1'}],
                            [{'datasetGroupArn': 'g1'}],
                            [{'datasetGroupArn': 'g1'}, {'datasetGroupArn': 'g1'}], [{}]]
    assert [fn(ctx)['usage'] for _, _, fn in PERSONALIZE_CHECKS] == [1, 2, 1, 2, 1]


def test_sagemaker_resource_counts():
    ctx = Mock()
    ctx.call.side_effect = [[{}], [{}, {}], [{}], [{}, {}, {}]]
    assert [fn(ctx)['usage'] for _, _, fn in SAGEMAKER_CHECKS] == [1, 2, 1, 3]
