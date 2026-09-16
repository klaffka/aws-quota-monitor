"""Amazon MQ per-broker quotas, all served by one DescribeBroker per broker."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import mq
from modules.qmcore.aws import CheckContext, NoData


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'mq', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _name, fn in mq.CHECKS if quota == code)


SUMMARIES = {'BrokerSummaries': [
    {'BrokerId': 'b-simple', 'DeploymentMode': 'SINGLE_INSTANCE', 'EngineType': 'ACTIVEMQ'},
    {'BrokerId': 'b-ldap', 'DeploymentMode': 'SINGLE_INSTANCE', 'EngineType': 'ACTIVEMQ'}]}
DETAILS = {
    'b-simple': {'BrokerId': 'b-simple', 'AuthenticationStrategy': 'SIMPLE',
                 'SecurityGroups': ['sg-1'], 'Tags': {'a': '1', 'b': '2'},
                 'Users': [{'Username': 'one'}, {'Username': 'two'}, {'Username': 'three'}]},
    'b-ldap': {'BrokerId': 'b-ldap', 'AuthenticationStrategy': 'LDAP',
               'SecurityGroups': ['sg-1', 'sg-2'], 'Tags': {'a': '1'},
               'Users': [{'Username': 'ldap-cached'}]}}


def stub_brokers(stub):
    stub.add_response('list_brokers', SUMMARIES, {})
    for identifier, detail in DETAILS.items():
        stub.add_response('describe_broker', detail, {'BrokerId': identifier})


@pytest.mark.parametrize('code, expected, owner', [
    ('L-8113B3FA', 2, 'b-ldap'),
    ('L-014B4583', 2, 'b-simple'),
])
def test_per_broker_quotas_use_the_largest_broker(code, expected, owner):
    ctx = context(code)
    with Stubber(ctx.client('mq')) as stub:
        stub_brokers(stub)
        result = check(code)(ctx)
        assert (result['usage'], result['resource_id']) == (expected, owner)
        stub.assert_no_pending_responses()


def test_only_simple_auth_brokers_count_their_users():
    """An LDAP broker's users live in the directory, not against this quota."""
    ctx = context('L-D505D03E')
    with Stubber(ctx.client('mq')) as stub:
        stub_brokers(stub)
        result = check('L-D505D03E')(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'b-simple')
        stub.assert_no_pending_responses()


def test_the_broker_detail_is_fetched_once_for_every_per_broker_quota():
    """Three quotas read the same detail, so the cache must serve two of them."""
    ctx = context('L-8113B3FA')
    with Stubber(ctx.client('mq')) as stub:
        stub_brokers(stub)
        for code in ('L-8113B3FA', 'L-014B4583', 'L-D505D03E'):
            check(code)(ctx)
        stub.assert_no_pending_responses()


def test_a_broker_detail_for_another_broker_is_refused():
    ctx = context('L-014B4583')
    with Stubber(ctx.client('mq')) as stub:
        stub.add_response('list_brokers', {'BrokerSummaries': [
            {'BrokerId': 'asked', 'DeploymentMode': 'SINGLE_INSTANCE',
             'EngineType': 'ACTIVEMQ'}]}, {})
        stub.add_response('describe_broker', {'BrokerId': 'answered'}, {'BrokerId': 'asked'})
        with pytest.raises(NoData, match='different identity'):
            check('L-014B4583')(ctx)
