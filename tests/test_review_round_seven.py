from unittest.mock import Mock

from modules.qmchecks.location import CHECKS


def test_location_tracker_consumers_are_maximum_per_tracker():
    ctx = Mock()
    ctx.call.side_effect = [[{'TrackerName': 'tracker'}], [{'ConsumerArn': 'consumer'}]]
    result = next(check for code, _, check in CHECKS if code == 'L-7B55057C')(ctx)
    assert (result['usage'], result['resource_id']) == (1, 'tracker')
