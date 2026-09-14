from unittest.mock import Mock

from modules.qmchecks.location import CHECKS


def test_location_geofences_are_maximum_per_collection():
    ctx = Mock()
    ctx.call.side_effect = [[{'CollectionName': 'collection'}],
                            [{'GeofenceId': 'one'}, {'GeofenceId': 'two'}]]
    result = CHECKS[-1][2](ctx)
    assert (result['usage'], result['resource_id']) == (2, 'collection')
