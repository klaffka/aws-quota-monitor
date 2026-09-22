import boto3
import pytest
from moto import mock_aws
from botocore.httpsession import URLLib3Session
from modules.qmdb.db import QuotaLogDb


@pytest.fixture(autouse=True)
def isolated_aws(monkeypatch):
    for name in ('AWS_PROFILE', 'QM_AWS_PROFILE'):
        monkeypatch.delenv(name, raising=False)
    for key, value in {'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing',
                       'AWS_SESSION_TOKEN': 'testing', 'AWS_DEFAULT_REGION': 'eu-central-1',
                       'AWS_REGION': 'eu-central-1', 'AWS_EC2_METADATA_DISABLED': 'true'}.items():
        monkeypatch.setenv(key, value)
    def denied(*args, **kwargs):
        raise AssertionError('Unit tests must not make AWS network requests')
    monkeypatch.setattr(URLLib3Session, 'send', denied)


@pytest.fixture
def aws_db(monkeypatch):
    with mock_aws():
        session = boto3.Session(region_name='eu-central-1')
        table = session.resource('dynamodb').create_table(TableName='test-quota-table',
            KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST')
        monkeypatch.setenv('QM_QUOTA_TABLE', table.name)
        yield session, QuotaLogDb(session)
