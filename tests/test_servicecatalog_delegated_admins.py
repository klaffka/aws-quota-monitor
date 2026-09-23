"""Service Catalog delegated administrators, counted through Organizations."""
import boto3
import pytest
from botocore.stub import Stubber
from datetime import datetime, UTC

from modules.qmchecks import servicecatalog
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)


def context():
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'servicecatalog', 'QuotaCode': 'L-CA761021',
                          'Value': 5}], account='123456789012')


def check():
    return next(fn for code, _name, fn in servicecatalog.CHECKS if code == 'L-CA761021')


def administrator(identity):
    return {'Id': identity, 'Arn': f'arn:aws:organizations::1:account/o-x/{identity}',
            'Email': f'{identity}@example.com', 'Name': identity, 'Status': 'ACTIVE',
            'JoinedMethod': 'CREATED', 'JoinedTimestamp': MOMENT,
            'DelegationEnabledDate': MOMENT}


def test_only_service_catalogs_delegated_administrators_are_counted():
    """Organizations answers per service principal, so the principal is named."""
    ctx = context()
    with Stubber(ctx.client('organizations')) as stub:
        stub.add_response('list_delegated_administrators',
                          {'DelegatedAdministrators': [administrator('111111111111'),
                                                       administrator('222222222222')]},
                          {'ServicePrincipal': 'servicecatalog.amazonaws.com'})
        result = check()(ctx)
        assert (result['usage'], result['method']) == (2, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_an_account_that_is_not_an_organization_reports_no_data():
    """A standalone account cannot answer the question at all."""
    ctx = context()
    with Stubber(ctx.client('organizations')) as stub:
        stub.add_client_error('list_delegated_administrators',
                              service_error_code='AWSOrganizationsNotInUseException',
                              http_status_code=400)
        with pytest.raises(NoData, match='organization'):
            check()(ctx)
