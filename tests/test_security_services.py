from unittest.mock import Mock

from modules.qmchecks.access_analyzer import analyzer_count, archive_rules_per_analyzer
from modules.qmchecks.guardduty import detector_count, sets_per_detector
from modules.qmchecks.securityhub import CHECKS


def test_access_analyzer_counts_types_and_archive_rules_per_analyzer():
    ctx = Mock()
    ctx.call.return_value = [
        {'type': 'ACCOUNT', 'arn': 'arn:account'}, {'type': 'ORGANIZATION', 'arn': 'arn:org'}]
    assert analyzer_count(ctx, 'ACCOUNT')['usage'] == 1
    ctx.call.side_effect = [
        [{'type': 'ACCOUNT', 'arn': 'arn:account'}, {'type': 'ORGANIZATION', 'arn': 'arn:org'}],
        [{'id': 'rule-1'}, {'id': 'rule-2'}], [{'id': 'rule-3'}],
    ]
    result = archive_rules_per_analyzer(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'arn:account')


def test_guardduty_detector_and_set_counts_use_maximum_per_detector():
    ctx = Mock()
    ctx.call.return_value = ['detector-a', 'detector-b']
    assert detector_count(ctx)['usage'] == 2
    ctx.call.side_effect = [['detector-a', 'detector-b'], ['a'], ['a', 'b']]
    result = sets_per_detector(ctx, 'list_ip_sets', 'IpSets', 'guardduty:ListIPSets')
    assert (result['usage'], result['resource_id']) == (2, 'detector-b')


def test_securityhub_checks_use_paginated_resource_inventories():
    ctx = Mock()
    def calls(service, method, key=None, **kwargs):
        if method == 'get_invitations_count':
            return {'InvitationsCount': 2}
        return [{'id': 'one'}, {'id': 'two'}]
    ctx.call.side_effect = calls
    for _, _, check in CHECKS:
        assert check(ctx)['usage'] == 2
