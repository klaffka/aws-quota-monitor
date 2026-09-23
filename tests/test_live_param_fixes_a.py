"""API parameters the first live collector run rejected."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iotcore
from modules.qmchecks.vpc import vpc
from modules.qmcore.aws import CheckContext


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def test_block_public_access_exclusions_page_with_max_results():
    """EC2 needs ExclusionIds or MaxResults; MaxResults keeps the NextToken walk."""
    ctx = context('vpc', 'L-42B9C2CA')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_vpc_block_public_access_exclusions', {
            'VpcBlockPublicAccessExclusions': [
                {'ExclusionId': 'e1', 'State': 'create-complete'},
                {'ExclusionId': 'e2', 'State': 'delete-complete'}],
            'NextToken': 'next'}, {'MaxResults': 1000})
        stub.add_response('describe_vpc_block_public_access_exclusions', {
            'VpcBlockPublicAccessExclusions': [
                {'ExclusionId': 'e3', 'State': 'update-in-progress'}]},
            {'MaxResults': 1000, 'NextToken': 'next'})
        assert check('L-42B9C2CA', vpc.CHECKS)(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_unconfigured_iot_logging_has_no_logging_levels():
    """AWS states no level was ever set, which is a zero inventory."""
    ctx = context('iotcore', 'L-E1FD4738')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_client_error('list_v2_logging_levels', 'NotConfiguredException',
                              'SetV2LoggingOptions was not previously called. '
                              'No logging levels have been set.', 400, expected_params={})
        result = check('L-E1FD4738', iotcore.CHECKS)(ctx)
    assert (result['usage'], result['method']) == (0, 'ACCOUNT_COUNT')


def test_iot_logging_levels_are_counted_and_other_errors_propagate():
    ctx = context('iotcore', 'L-E1FD4738')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_v2_logging_levels', {'logTargetConfigurations': [
            {'logTarget': {'targetType': 'THING_GROUP', 'targetName': 'a'}, 'logLevel': 'INFO'},
            {'logTarget': {'targetType': 'CLIENT_ID', 'targetName': 'b'}, 'logLevel': 'ERROR'}]}, {})
        assert check('L-E1FD4738', iotcore.CHECKS)(ctx)['usage'] == 2
    denied = context('iotcore', 'L-E1FD4738')
    with Stubber(denied.client('iot')) as stub:
        stub.add_client_error('list_v2_logging_levels', 'AccessDeniedException', 'denied',
                              403, expected_params={})
        with pytest.raises(Exception, match='AccessDenied'):
            check('L-E1FD4738', iotcore.CHECKS)(denied)
