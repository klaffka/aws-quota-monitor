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
    # The job-scoped checks descend into a job definition and are covered by
    # tests/test_gamelift_macie_inventories.py against a real client.
    scoped = {'L-14954719', 'L-3572300B'}
    assert all(check(ctx)['usage'] == 2
               for code, _name, check in MACIE_CHECKS if code not in scoped)


def test_transfer_checks_use_paginated_resource_keys():
    """Every Transfer check reads a list key, and the scoped ones pick a parent.

    The two servers differ in identity provider on purpose: service-managed
    users and directory accesses live on one server each, so a check that
    ignored the provider would count both and report twice the usage.
    """
    ctx = Mock()
    def calls(service, method, key=None, **kwargs):
        if method == 'list_servers':
            return [{'ServerId': 'one', 'EndpointType': 'VPC_ENDPOINT',
                     'IdentityProviderType': 'SERVICE_MANAGED'},
                    {'ServerId': 'two', 'EndpointType': 'VPC_ENDPOINT',
                     'IdentityProviderType': 'AWS_DIRECTORY_SERVICE'}]
        if method == 'list_users':
            return [{'UserName': 'user-one', 'SshPublicKeyCount': 1},
                    {'UserName': 'user-two', 'SshPublicKeyCount': 4}]
        if method == 'describe_user':
            return {'User': {'HomeDirectoryDetails': [{}, {}, {}]}}
        if method == 'list_profiles':
            return [{'ProfileId': 'p-one'}, {'ProfileId': 'p-two'}]
        if method == 'describe_profile':
            return {'Profile': {'ProfileId': kwargs['ProfileId'], 'CertificateIds': [{}]}}
        if method == 'list_connectors':
            return [{'ConnectorType': 'AS2'}, {'ConnectorType': 'SFTP'}]
        return [{'id': 'one'}, {'id': 'two'}]
    ctx.call.side_effect = calls
    usage = {code: check(ctx)['usage'] for code, _name, check in TRANSFER_CHECKS}

    # Account-wide listings return the two entries the fake holds.
    assert [usage[code] for code in ('L-7E767654', 'L-858EB316', 'L-8A2575E3',
                                     'L-6E386A05', 'L-C0FDC60E', 'L-A6509B77',
                                     'L-5BAD02C2')] == [2] * 7
    # Agreements are listed per server, so two servers of two agreements make four.
    assert usage['L-C08739CA'] == 4
    assert (usage['L-547461C3'], usage['L-D0C40802']) == (1, 1)
    assert usage['L-101C3D29'] == 2
    assert usage['L-2F6B27A1'] == 3
    assert usage['L-B2750988'] == 1
    # Only the service-managed server holds users, and only the directory-backed
    # one holds accesses; both would be 2 if the provider were ignored.
    assert usage['L-90797EDA'] == 4
    assert usage['L-843894CE'] == 2
