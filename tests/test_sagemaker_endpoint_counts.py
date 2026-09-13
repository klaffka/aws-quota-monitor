from unittest.mock import Mock

from modules.qmchecks.sagemaker_resources import ALL_CHECKS


def test_sagemaker_active_endpoint_instances_are_aggregated():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'EndpointName': 'one', 'EndpointStatus': 'InService'},
         {'EndpointName': 'deleted', 'EndpointStatus': 'Deleted'}],
        {'EndpointConfigName': 'config-one'},
        [{'InitialInstanceCount': 2}, {'InitialInstanceCount': 3}],
    ]
    check = next(fn for code, _, fn in ALL_CHECKS if code == 'L-7A3DF611')
    assert check(ctx)['usage'] == 5
