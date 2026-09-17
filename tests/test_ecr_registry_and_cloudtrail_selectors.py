"""ECR replication configuration and CloudTrail event selector scopes."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import cloudtrail, ecr
from modules.qmcore.aws import CheckContext, NoData


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def rule(destinations, filters=0):
    return {'destinations': [{'region': region, 'registryId': '123456789012'}
                             for region in destinations],
            'repositoryFilters': [{'filter': f'team{index}', 'filterType': 'PREFIX_MATCH'}
                                  for index in range(filters)]}


REGISTRY = {'registryId': '123456789012', 'replicationConfiguration': {'rules': [
    rule(['eu-west-1', 'us-east-1'], filters=3),
    rule(['us-east-1'], filters=1)]}}


@pytest.mark.parametrize('code, expected', [
    ('L-9B60BFFB', 2),   # rules in the configuration
    ('L-241DEEBA', 3),   # filters on the busiest rule
    ('L-24725E9A', 2),   # distinct destinations across every rule
])
def test_one_registry_call_answers_all_three_replication_quotas(code, expected):
    """us-east-1 appears in both rules and is still one destination."""
    ctx = context('ecr', code)
    with Stubber(ctx.client('ecr')) as stub:
        stub.add_response('describe_registry', REGISTRY, {})
        assert check(code, ecr.CHECKS)(ctx)['usage'] == expected
        stub.assert_no_pending_responses()


def test_a_registry_without_replication_counts_as_zero():
    ctx = context('ecr', 'L-9B60BFFB')
    with Stubber(ctx.client('ecr')) as stub:
        stub.add_response('describe_registry',
                          {'registryId': '123456789012',
                           'replicationConfiguration': {'rules': []}}, {})
        assert check('L-9B60BFFB', ecr.CHECKS)(ctx)['usage'] == 0


def trail(name):
    return {'Name': name, 'TrailARN': f'arn:aws:cloudtrail:eu-central-1:123456789012:trail/{name}',
            'HomeRegion': 'eu-central-1'}


def selectors(name, data_resources=0, advanced=()):
    answer = {'TrailARN': f'arn:aws:cloudtrail:eu-central-1:123456789012:trail/{name}'}
    if advanced:
        answer['AdvancedEventSelectors'] = [
            {'Name': f'sel{index}',
             'FieldSelectors': [{'Field': 'eventCategory', 'Equals': ['Management']}] * count}
            for index, count in enumerate(advanced)]
    else:
        answer['EventSelectors'] = [{
            'ReadWriteType': 'All', 'IncludeManagementEvents': True,
            'DataResources': [{'Type': 'AWS::S3::Object', 'Values': ['arn:aws:s3:::b/']}
                              for _ in range(data_resources)]}]
    return answer


def test_event_selectors_and_their_data_resources_come_from_one_call():
    ctx = context('cloudtrail', 'L-71DEA5C6')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [trail('one'), trail('two')]}, {})
        stub.add_response('get_event_selectors', selectors('one', data_resources=4),
                          {'TrailName': 'one'})
        stub.add_response('get_event_selectors', selectors('two', data_resources=1),
                          {'TrailName': 'two'})
        result = check('L-71DEA5C6', cloudtrail.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'one')
        stub.assert_no_pending_responses()


def test_conditions_are_summed_across_a_trails_advanced_selectors():
    """The quota bounds the conditions across all of them, not per selector."""
    ctx = context('cloudtrail', 'L-203ED99D')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [trail('one')]}, {})
        stub.add_response('get_event_selectors', selectors('one', advanced=(2, 3)),
                          {'TrailName': 'one'})
        result = check('L-203ED99D', cloudtrail.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'one')
        stub.assert_no_pending_responses()


def test_a_trail_without_a_name_is_reported():
    ctx = context('cloudtrail', 'L-9387CED7')
    with Stubber(ctx.client('cloudtrail')) as stub:
        stub.add_response('describe_trails', {'trailList': [{'HomeRegion': 'eu-central-1'}]}, {})
        with pytest.raises(NoData, match='name'):
            check('L-9387CED7', cloudtrail.CHECKS)(ctx)
