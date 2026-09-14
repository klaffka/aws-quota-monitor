from unittest.mock import Mock

from modules.qmchecks.cloudwatchpredictions import CHECKS


def test_ba_cloudwatch_anomaly_models_are_counted():
    ctx = Mock()
    ctx.call.return_value = [{'Namespace': 'AWS/Lambda'}, {'Namespace': 'AWS/EC2'}]
    assert CHECKS[0][2](ctx)['usage'] == 2
