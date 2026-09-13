from unittest.mock import Mock

from modules.qmchecks.internetmonitor import resources_per_monitor
from modules.qmchecks.kinesisanalytics import CHECKS as KINESIS_ANALYTICS_CHECKS
from modules.qmchecks.imagebuilder import CHECKS as IMAGEBUILDER_CHECKS
from modules.qmchecks.oam import CHECKS as OAM_CHECKS
from modules.qmchecks.kafka import CHECKS as KAFKA_CHECKS, configuration_revisions
from modules.qmchecks.license_manager import CHECKS as LICENSE_CHECKS
from modules.qmchecks.kinesis_resources import shard_count
from modules.qmchecks.rekognition import project_policies_per_project


def test_internet_monitor_resources_use_maximum_per_monitor():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'MonitorName': 'one'}, {'MonitorName': 'two'}],
        [{'Resource': 'a'}],
        [{'Resource': 'a'}, {'Resource': 'b'}, {'Resource': 'c'}],
    ]
    result = resources_per_monitor(ctx)
    assert (result['usage'], result['resource_id']) == (3, 'two')


def test_kinesis_analytics_application_count_is_paginated():
    ctx = Mock()
    ctx.call.return_value = [{'ApplicationName': 'one'}, {'ApplicationName': 'two'}]
    assert KINESIS_ANALYTICS_CHECKS[0][2](ctx)['usage'] == 2


def test_imagebuilder_and_oam_inventory_counts_use_paginated_lists():
    ctx = Mock()
    ctx.call.return_value = [{'arn': 'one'}, {'arn': 'two'}]
    assert [check(ctx)['usage'] for _, _, check in IMAGEBUILDER_CHECKS] == [2, 2, 2]
    assert OAM_CHECKS[1][2](ctx)['usage'] == 2


def test_kafka_broker_quota_sums_provisioned_brokers():
    ctx = Mock()
    ctx.call.return_value = [
        {'Provisioned': {'NumberOfBrokerNodes': 3}},
        {'Provisioned': {'NumberOfBrokerNodes': 2}},
    ]
    check = next(fn for code, _, fn in KAFKA_CHECKS if code == 'L-EDD31C36')
    assert check(ctx)['usage'] == 5


def test_kafka_configuration_revisions_use_maximum_per_configuration():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'Arn': 'arn:one'}, {'Arn': 'arn:two'}],
        [{'Revision': 1}, {'Revision': 2}],
        [{'Revision': 1}],
    ]
    assert configuration_revisions(ctx)['usage'] == 2


def test_license_manager_counts_use_paginated_lists():
    ctx = Mock()
    ctx.call.return_value = [{'id': 'one'}, {'id': 'two'}]
    assert [check(ctx)['usage'] for _, _, check in LICENSE_CHECKS] == [2, 2]


def test_kinesis_shard_count_sums_shards_across_streams():
    ctx = Mock()
    ctx.call.side_effect = [
        ['stream-a', 'stream-b'],
        [{'ShardId': 'a1'}, {'ShardId': 'a2'}],
        [{'ShardId': 'b1'}],
    ]
    assert shard_count(ctx)['usage'] == 3


def test_rekognition_project_policies_use_maximum_per_project():
    ctx = Mock()
    ctx.call.side_effect = [
        [{'ProjectArn': 'one'}, {'ProjectArn': 'two'}],
        [{'PolicyName': 'a'}],
        [{'PolicyName': 'a'}, {'PolicyName': 'b'}],
    ]
    result = project_policies_per_project(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'two')
