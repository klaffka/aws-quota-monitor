"""Checks whose first live run failed on endpoint Region or an error code."""
from unittest.mock import Mock

import boto3
from botocore.stub import Stubber

from modules.qmchecks import lightsail, s3
from modules.qmcore.aws import CheckContext

ACCOUNT = '123456789012'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1',
                                      aws_access_key_id='test', aws_secret_access_key='test'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 50}],
                        account=ACCOUNT)


def only(module, code):
    return [entry for entry in module.CHECKS if entry[0] == code]


def test_in_region_binds_clients_to_the_fixed_region_and_keeps_its_own_cache():
    ctx = context('lightsail', 'L-1DB37119')
    pinned = ctx.in_region('us-east-1')
    assert ctx.in_region('eu-central-1') is ctx
    assert ctx.in_region('us-east-1') is pinned
    assert pinned.client('lightsail').meta.region_name == 'us-east-1'
    assert ctx.client('lightsail').meta.region_name == 'eu-central-1'
    assert pinned.cache is not ctx.cache


def test_in_region_keeps_a_replaced_call():
    ctx = context('lightsail', 'L-1DB37119')
    ctx.call = Mock(return_value=[])
    assert ctx.in_region('us-east-1').call is ctx.call


def test_lightsail_distributions_are_read_from_us_east_1():
    # Distribution APIs answer only in us-east-1, whatever Region the collector runs in.
    distributions = [{'name': 'edge', 'alternativeDomainNames': ['a.example', 'b.example']},
                     {'name': 'other', 'alternativeDomainNames': []}]
    for code, usage in (('L-1DB37119', 2), ('L-C27ADEB6', 2), ('L-9A462869', 0),
                        ('L-C3D6EA9E', 0), ('L-97957401', 0), ('L-A85C5367', 0)):
        ctx = context('lightsail', code)
        with Stubber(ctx.in_region('us-east-1').client('lightsail')) as stub:
            stub.add_response('get_distributions', {'distributions': distributions}, {})
            result, = ctx.run('lightsail', only(lightsail, code))
            stub.assert_no_pending_responses()
        assert (result['qualityStatus'], result['usageValue'], result['region']) == (
            'OK', usage, 'eu-central-1'), code


def test_multi_region_access_points_are_read_from_us_west_2():
    ctx = context('s3', 'L-881EA1F4')
    client = ctx.in_region('us-west-2').client('s3control')
    assert client.meta.region_name == 'us-west-2'
    with Stubber(client) as stub:
        stub.add_response('list_multi_region_access_points',
                          {'AccessPoints': [{'Name': 'one'}, {'Name': 'two'}]},
                          {'AccountId': ACCOUNT})
        result, = ctx.run('s3', only(s3, 'L-881EA1F4'))
        stub.assert_no_pending_responses()
    assert (result['qualityStatus'], result['usageValue']) == ('OK', 2)


def _replication(second_error=None):
    ctx = context('s3', 'L-B461D596')
    with Stubber(ctx.client('s3')) as stub:
        stub.add_response('list_buckets', {'Buckets': [{'Name': 'plain'}, {'Name': 'copied'}]})
        stub.add_client_error('get_bucket_replication', 'ReplicationConfigurationNotFoundError',
                              'The replication configuration was not found', 404,
                              expected_params={'Bucket': 'plain'})
        if second_error:
            stub.add_client_error('get_bucket_replication', second_error, 'Access Denied', 403,
                                  expected_params={'Bucket': 'copied'})
        else:
            stub.add_response('get_bucket_replication', {'ReplicationConfiguration': {
                'Role': 'arn:aws:iam::123456789012:role/r',
                'Rules': [{'Status': 'Enabled', 'Destination': {'Bucket': 'arn:aws:s3:::d'}}] * 2}},
                {'Bucket': 'copied'})
        result, = ctx.run('s3', only(s3, 'L-B461D596'))
        stub.assert_no_pending_responses()
    return result


def test_a_bucket_without_replication_has_zero_rules():
    result = _replication()
    assert (result['qualityStatus'], result['usageValue'], result['maxResourceId']) == (
        'OK', 2, 'copied')


def test_other_replication_errors_still_fail_the_check():
    assert _replication('AccessDenied')['qualityStatus'] == 'ERROR'
