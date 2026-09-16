from unittest.mock import Mock

from modules.qmchecks.location import CHECKS as LOCATION
from modules.qmchecks.appintegrations import CHECKS as APPINTEGRATIONS
from modules.qmchecks.iotevents import CHECKS as IOTEVENTS
from modules.qmchecks.iotanalytics import CHECKS as IOTANALYTICS


def test_round_two_resource_count_checks_use_paginated_inventory_results():
    location = Mock()
    location.call.side_effect = [[{}], [{}], [{}], [{}], [{}], [{}],
                                  [{'TrackerName': 'tracker'}],
                                  [{'ConsumerArn': 'consumer'}],
                                  [{'CollectionName': 'collection'}],
                                  [{}]]
    assert [check[2](location)['usage'] for check in LOCATION] == [1] * len(LOCATION)

    for checks in (APPINTEGRATIONS, IOTEVENTS):
        context = Mock()
        context.call.return_value = [{}]
        assert checks[0][2](context)['usage'] == 1

    iotanalytics = Mock()
    iotanalytics.call.side_effect = [[{}]] * len(IOTANALYTICS)
    assert [check[2](iotanalytics)['usage'] for check in IOTANALYTICS] == [1] * len(IOTANALYTICS)
