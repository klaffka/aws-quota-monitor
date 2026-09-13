from unittest.mock import Mock

from modules.qmchecks.application_autoscaling import CHECKS


def test_application_autoscaling_targets_are_counted_by_namespace():
    ctx = Mock()
    ctx.call.return_value = [{'ResourceId': 'service/default'}]
    result = CHECKS[1][2](ctx)
    assert result['usage'] == 1
    assert ctx.call.call_args.kwargs['ServiceNamespace'] == 'ecs'
