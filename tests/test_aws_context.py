from datetime import UTC
import pytest


def test_the_call_cache_accepts_datetime_arguments():
    """Several APIs take a time window, which the cache key must survive."""
    from datetime import datetime

    import boto3
    from botocore.stub import Stubber

    from modules.qmcore.aws import CheckContext

    moment = datetime(2026, 9, 15, tzinfo=UTC)
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'),
                       account='123456789012', now=moment)
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_audit_tasks', {'tasks': [{'taskId': 't1'}]},
                          {'startTime': moment, 'endTime': moment})
        first = ctx.call('iot', 'list_audit_tasks', 'tasks',
                         startTime=moment, endTime=moment)
        # The second call is served from the cache, so the stub sees one request.
        second = ctx.call('iot', 'list_audit_tasks', 'tasks',
                          startTime=moment, endTime=moment)
        assert first == second == [{'taskId': 't1'}]
        stub.assert_no_pending_responses()


def test_paginate_follows_the_service_catalog_page_token():
    """NextPageToken comes back as PageToken; a missed page undercounts silently."""
    from unittest.mock import Mock

    from modules.qmcore.aws import paginate

    client = Mock()
    client.can_paginate.return_value = False
    client.list_portfolio_access.side_effect = [
        {'AccountIds': ['111111111111'], 'NextPageToken': 'next'},
        {'AccountIds': ['222222222222']},
    ]
    assert paginate(client, 'list_portfolio_access', 'AccountIds',
                    PortfolioId='port-1') == ['111111111111', '222222222222']
    assert client.list_portfolio_access.call_args.kwargs == {
        'PortfolioId': 'port-1', 'PageToken': 'next'}


def test_paginate_follows_the_lightsail_next_page_token():
    """Lightsail spells the cursor nextPageToken; page two was dropped silently."""
    from unittest.mock import Mock

    from modules.qmcore.aws import paginate

    client = Mock()
    client.can_paginate.return_value = False
    client.get_distributions.side_effect = [
        {'distributions': [{'name': 'one'}], 'nextPageToken': 'next'},
        {'distributions': [{'name': 'two'}]},
    ]
    assert paginate(client, 'get_distributions', 'distributions') == [
        {'name': 'one'}, {'name': 'two'}]
    assert client.get_distributions.call_args.kwargs == {'pageToken': 'next'}


# Answers recorded from the first live run on 2026-09-23.
NOT_SET_UP = [
    ('AccessDeniedException', 'ListPolicies',
     'No default admin could be found for account 123456789012 in Region eu-central-1', 'NO_DATA'),
    ('AccessDeniedException', 'ListLicenses',
     ('Service role not found. Consult setup procedures in License Manager User Guide and '
     'create the required role for the service.'), 'NO_DATA'),
    ('AccessDeniedException', 'ListClassificationJobs', 'Macie is not enabled.', 'NO_DATA'),
    ('AccessDeniedException', 'ListAssessments', ('Please complete AWS Audit Manager setup from '
     'home page to enable this action in this account.'), 'NO_DATA'),
    ('UninitializedAccountException', 'DescribeSourceServers', 'Account not initialized', 'NO_DATA'),
    ('UnsupportedUserEditionException', 'ListAnalyses',
     'Account 123456789012 is not subscribed for QuickSight', 'NO_DATA'),
    ('ValidationException', 'ListRotations',
     'Invalid value provided - Account not found for the request', 'NO_DATA'),
    ('OptInRequiredException', 'ListAutomationEvents',
     'Aws account is not registered for recommendation.', 'NO_DATA'),
    ('TagOptionNotMigratedException', 'ListTagOptions', 'TagOption Migration not complete', 'NO_DATA'),
    ('InvalidOperationException', 'ListAdminAccountsForOrganization',
     ('123456789012 is not the management account of the Organization but is attempting to '
     'perform an action that only the Organization management account can perform.'), 'NO_DATA'),
    ('AccessDeniedException', 'ListAutomationRules',
     'Account 123456789012 is not authorized to perform this operation', 'NO_DATA'),
    ('403', 'ListSolNetworkPackages',
     'AWS Telco Network Builder is deprecated. All API operations are blocked.', 'UNSUPPORTED'),
    ('UnauthorizedException', 'ListSecurityProfiles',
     ('This feature is no longer available to new customers. For more information, see '
     'https://docs.aws.amazon.com/iot-device-defender/latest/devguide/dd-detect-availability-change.html'),
     'UNSUPPORTED'),
    ('AccessDeniedException', 'GetDevEndpoints',
     'GetDevEndpoints operation is currently disabled.', 'UNSUPPORTED'),
    ('AccessDeniedException', 'ListStateTemplates',
     'Account is not authorized to use this feature.', 'UNSUPPORTED'),
]


def _run_failing(code, operation, message):
    from unittest.mock import Mock

    from botocore.exceptions import ClientError

    from modules.qmcore.aws import CheckContext

    ctx = CheckContext(Mock(region_name='eu-central-1'), account='123456789012',
                       quotas=[{'ServiceCode': 'svc', 'QuotaCode': 'L-1', 'Value': 10}])

    def check(_):
        raise ClientError({'Error': {'Code': code, 'Message': message}}, operation)

    result, = ctx.run('svc', [('L-1', 'quota', check)])
    return result


@pytest.mark.parametrize('code, operation, message, status', NOT_SET_UP)
def test_a_service_the_account_has_not_set_up_is_not_an_error(code, operation, message, status):
    """These answers carry no usage, but they are not failures of the check either."""
    result = _run_failing(code, operation, message)
    assert result['qualityStatus'] == status
    assert message in result['qualityReason']


@pytest.mark.parametrize('code, operation, message', [
    # A missing IAM grant must stay visible.
    ('AccessDeniedException', 'ListKeyspaces',
     ('User: arn:aws:sts::123456789012:assumed-role/qm-quotacontroller-exec/qm-quota-collector '
     'is not authorized to perform: cassandra:Select on resource: arn:aws:cassandra:eu-central-1:'
     '123456789012:/keyspace/*')),
    ('AccessDeniedException', 'ListStreamProcessors', ''),
    # The Security Hub wording is only known to mean "not the administrator" here.
    ('AccessDeniedException', 'ListFindings',
     'Account 123456789012 is not authorized to perform this operation'),
    ('ValidationException', 'ListRotations', 'Invalid value provided'),
])
def test_other_denials_stay_errors(code, operation, message):
    assert _run_failing(code, operation, message)['qualityStatus'] == 'ERROR'
