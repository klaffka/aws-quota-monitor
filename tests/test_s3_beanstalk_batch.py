from unittest.mock import Mock

from modules.qmchecks.elasticbeanstalk import CHECKS as EB_CHECKS
from modules.qmchecks.batch import CHECKS as BATCH_CHECKS
from modules.qmchecks.s3 import CHECKS as S3_CHECKS


def test_elastic_beanstalk_counts_resources():
    ctx = Mock()
    def call(_service, method, key=None, **kwargs):
        return ([{}, {}] if method == 'describe_environments' else [{}])
    ctx.call.side_effect = call
    assert [fn(ctx)['usage'] for _, _, fn in EB_CHECKS] == [1, 2, 1, 1]


def test_batch_counts_queues_and_max_environments_per_queue():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'jobQueueArn': 'q1', 'computeEnvironmentOrder': [{}, {}]},
         {'jobQueueArn': 'q2', 'computeEnvironmentOrder': [{}]}],
        [{}, {}, {}],
    ]
    assert BATCH_CHECKS[0][2](ctx)['usage'] == 2
    assert BATCH_CHECKS[1][2](ctx)['usage'] == 3
    # Each check has an independent inventory call; provide fresh responses.
    ctx.call.side_effect = [[
        {'jobQueueArn': 'q1', 'computeEnvironmentOrder': [{}, {}]},
        {'jobQueueArn': 'q2', 'computeEnvironmentOrder': [{}]},
    ]]
    assert BATCH_CHECKS[2][2](ctx)['usage'] == 2


def test_s3_control_counts_access_points():
    ctx = Mock(account='123456789012')
    ctx.call.side_effect = [
        [{'Name': 'bucket'}],
        {'ReplicationConfiguration': {'Rules': [{}]}},
        [{'Name': 'bucket'}],
        {'Rules': [{}]},
        [{}, {}],
    ]
    checks = {code: fn for code, _, fn in S3_CHECKS}
    assert checks['L-B461D596'](ctx)['usage'] == 1
    assert checks['L-146D5F0C'](ctx)['usage'] == 1
    assert checks['L-FAABEEBA'](ctx)['usage'] == 2
