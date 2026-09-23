import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import lightsail
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

INSTANCE = 'web-1'
SERVICE = 'api'
OTHER_SERVICE = 'worker'
DISTRIBUTION = 'edge'


def context(code='L-1DB37119'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'lightsail', 'QuotaCode': code, 'Value': 50}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in lightsail.CHECKS if quota == code)


def disk(name, size, attached=None):
    result = {'name': name, 'sizeInGb': size, 'state': 'in-use'}
    if attached is not None:
        result['attachedTo'] = attached
    return result


def test_disks_are_reported_per_instance_by_size_and_by_attached_total():
    disks = [disk('d1', 8, INSTANCE), disk('d2', 16, INSTANCE),
             disk('d3', 64, 'web-2'), disk('d4', 32)]
    for code, expected_usage, expected_id in (('L-6A41A279', 2, INSTANCE),
                                              ('L-8F295028', 64, 'd3'),
                                              ('L-9773709E', 88, None)):
        ctx = context(code)
        with Stubber(ctx.client('lightsail')) as stub:
            stub.add_response('get_disks', {'disks': disks}, {})
            result = check(code)(ctx)
            assert result['usage'] == expected_usage, code
            assert result.get('resource_id') == expected_id, code
            stub.assert_no_pending_responses()


def test_a_disk_without_a_size_raises_nodata():
    ctx = context('L-8F295028')
    with Stubber(ctx.client('lightsail')) as stub:
        stub.add_response('get_disks', {'disks': [{'name': 'd1', 'state': 'available'}]}, {})
        with pytest.raises(NoData, match='no size'):
            check('L-8F295028')(ctx)


def test_only_issued_certificates_count_as_active():
    ctx = context('L-D3506055')
    with Stubber(ctx.client('lightsail')) as stub:
        stub.add_response('get_certificates', {'certificates': [
            {'certificateName': 'a', 'domainName': 'a.example',
             'certificateDetail': {'name': 'a', 'status': 'ISSUED'}},
            {'certificateName': 'b', 'domainName': 'b.example',
             'certificateDetail': {'name': 'b', 'status': 'PENDING_VALIDATION'}},
            {'certificateName': 'c', 'domainName': 'c.example',
             'certificateDetail': {'name': 'c', 'status': 'EXPIRED'}}]}, {})
        assert lightsail.active_certificates(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_an_unknown_certificate_status_raises_nodata():
    ctx = context('L-D3506055')
    with Stubber(ctx.client('lightsail')) as stub:
        stub.add_response('get_certificates', {'certificates': [
            {'certificateName': 'a', 'certificateDetail': {'status': 'SPROUTING'}}]}, {})
        with pytest.raises(NoData, match='unknown status'):
            lightsail.active_certificates(ctx)


def container_service(name, scale=1, containers=0, domains=0):
    result = {'containerServiceName': name, 'scale': scale, 'power': 'nano',
              'state': 'READY'}
    if containers:
        result['currentDeployment'] = {'version': 1, 'state': 'ACTIVE', 'containers': {
            f'c{index}': {'image': 'nginx'} for index in range(containers)}}
    if domains:
        result['publicDomainNames'] = {
            'container': [f'host{index}.example' for index in range(domains)]}
    return result


def test_container_service_scale_containers_and_domains_are_counted():
    services = [container_service(SERVICE, scale=2, containers=3, domains=1),
                container_service(OTHER_SERVICE, scale=5, containers=1, domains=4)]
    for code, expected_usage, expected_id in (('L-C5DF431B', 5, OTHER_SERVICE),
                                              ('L-FC916C10', 3, SERVICE),
                                              ('L-8C5BE2E1', 4, OTHER_SERVICE)):
        ctx = context(code)
        with Stubber(ctx.client('lightsail')) as stub:
            stub.add_response('get_container_services',
                              {'containerServices': services}, {})
            result = check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def test_container_images_are_counted_per_service():
    ctx = context('L-B35F6366')
    with Stubber(ctx.client('lightsail')) as stub:
        stub.add_response('get_container_services', {'containerServices': [
            container_service(SERVICE), container_service(OTHER_SERVICE)]}, {})
        stub.add_response('get_container_images', {'containerImages': [
            {'image': ':api.web.1'}]}, {'serviceName': SERVICE})
        stub.add_response('get_container_images', {'containerImages': [
            {'image': ':worker.job.1'}, {'image': ':worker.job.2'}]},
            {'serviceName': OTHER_SERVICE})
        result = check('L-B35F6366')(ctx)
        assert (result['usage'], result['resource_id']) == (2, OTHER_SERVICE)
        stub.assert_no_pending_responses()


def distribution(name, domains=0, behaviors=0, cookies=0, headers=0, queries=0):
    return {'name': name, 'isEnabled': True,
            'alternativeDomainNames': [f'alt{index}.example' for index in range(domains)],
            'cacheBehaviors': [{'path': f'/p{index}', 'behavior': 'cache'}
                               for index in range(behaviors)],
            'cacheBehaviorSettings': {
                'forwardedCookies': {
                    'option': 'allow-list',
                    'cookiesAllowList': [f'c{index}' for index in range(cookies)]},
                'forwardedHeaders': {
                    'option': 'allow-list',
                    'headersAllowList': ['Accept'] * headers},
                'forwardedQueryStrings': {
                    'option': True,
                    'queryStringsAllowList': [f'q{index}' for index in range(queries)]}}}


def test_distribution_lists_are_reported_per_distribution():
    distributions = [distribution(DISTRIBUTION, domains=2, behaviors=1, cookies=3,
                                  headers=1, queries=0),
                     distribution('other', domains=1, behaviors=4, cookies=1,
                                  headers=2, queries=5)]
    for code, expected_usage, expected_id in (('L-C27ADEB6', 2, DISTRIBUTION),
                                              ('L-9A462869', 4, 'other'),
                                              ('L-C3D6EA9E', 3, DISTRIBUTION),
                                              ('L-97957401', 2, 'other'),
                                              ('L-A85C5367', 5, 'other')):
        ctx = context(code)
        with Stubber(ctx.in_region('us-east-1').client('lightsail')) as stub:
            stub.add_response('get_distributions', {'distributions': distributions}, {})
            result = check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (expected_usage,
                                                                expected_id), code
            stub.assert_no_pending_responses()


def test_every_lightsail_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'lightsail'}
    assert {code for code, _, _ in lightsail.CHECKS} <= registered
