from unittest.mock import Mock

from modules.qmchecks.inspector import suppression_rules
from modules.qmchecks.macie import CHECKS as MACIE_CHECKS
from modules.qmchecks.transfer import CHECKS as TRANSFER_CHECKS


def test_inspector_counts_only_suppression_filters():
    ctx = Mock()
    ctx.call.return_value = [
        {'action': 'SUPPRESS'}, {'action': 'SUPPRESS'}, {'action': 'NONE'}]
    assert len(suppression_rules(ctx)) == 2


def test_macie_checks_use_paginated_resource_keys():
    ctx = Mock()
    def calls(service, method, key=None, **kwargs):
        if method == 'get_invitations_count':
            return {'invitationsCount': 2}
        return [{'id': 'one'}, {'id': 'two'}]
    ctx.call.side_effect = calls
    assert all(check(ctx)['usage'] == 2 for _, _, check in MACIE_CHECKS)


def test_transfer_checks_use_paginated_resource_keys():
    ctx = Mock()
    def calls(service, method, key=None, **kwargs):
        if method == 'list_servers':
            return [{'ServerId': 'one', 'EndpointType': 'VPC_ENDPOINT'},
                    {'ServerId': 'two', 'EndpointType': 'VPC_ENDPOINT'}]
        if method == 'list_users':
            return [{'id': 'user-one'}, {'id': 'user-two'}]
        if method == 'list_connectors':
            return [{'ConnectorType': 'AS2'}, {'ConnectorType': 'SFTP'}]
        return [{'id': 'one'}, {'id': 'two'}]
    ctx.call.side_effect = calls
    usages = [check(ctx)['usage'] for _, _, check in TRANSFER_CHECKS]
    assert usages[:7] == [2] * 7
    assert usages[7:] == [1, 1, 2, 2, 0]
