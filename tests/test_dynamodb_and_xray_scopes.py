"""DynamoDB secondary indexes and X-Ray tags, both scoped to one parent."""
import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import dynamodb, xray
from modules.qmcore.aws import CheckContext, NoData

ACCOUNT = '123456789012'
REGION = 'eu-central-1'


def context(service, code):
    return CheckContext(boto3.Session(region_name=REGION),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account=ACCOUNT)


def check(module, code):
    return next(fn for quota, _name, fn in module.CHECKS if quota == code)


def stub_tables(stub, tables):
    """Stub the table listing, then one describe per table."""
    stub.add_response('list_tables', {'TableNames': list(tables)}, {})
    for name, indexes in tables.items():
        table = {'TableName': name}
        if indexes is not None:
            table['GlobalSecondaryIndexes'] = [
                {'IndexName': f'{name}-gsi{index}'} for index in range(indexes)]
        stub.add_response('describe_table', {'Table': table}, {'TableName': name})


def test_the_table_carrying_the_most_secondary_indexes_is_measured():
    ctx = context('dynamodb', 'L-F7858A77')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'quiet': 1, 'busy': 4})
        result = check(dynamodb, 'L-F7858A77')(ctx)
        assert (result['usage'], result['resource_id']) == (4, 'busy')
        stub.assert_no_pending_responses()


def test_a_table_without_secondary_indexes_counts_as_zero():
    """A table with no index still holds the quota, so it stays in the maximum."""
    ctx = context('dynamodb', 'L-F7858A77')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'plain': None})
        result = check(dynamodb, 'L-F7858A77')(ctx)
        assert (result['usage'], result['resource_id']) == (0, 'plain')
        stub.assert_no_pending_responses()


def test_an_account_without_tables_counts_as_zero():
    ctx = context('dynamodb', 'L-F7858A77')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub.add_response('list_tables', {'TableNames': []}, {})
        assert check(dynamodb, 'L-F7858A77')(ctx)['usage'] == 0
        stub.assert_no_pending_responses()


def test_the_table_listing_and_the_index_scope_share_one_call():
    ctx = context('dynamodb', 'L-F98FE922')
    with Stubber(ctx.client('dynamodb')) as stub:
        stub_tables(stub, {'one': 2, 'two': 0})
        assert check(dynamodb, 'L-F98FE922')(ctx)['usage'] == 2
        assert check(dynamodb, 'L-F7858A77')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def group_arn(name):
    return f'arn:aws:xray:{REGION}:{ACCOUNT}:group/{name}/1'


def rule_arn(name):
    return f'arn:aws:xray:{REGION}:{ACCOUNT}:sampling-rule/{name}'


def stub_group_tags(stub, groups):
    stub.add_response('get_groups', {'Groups': [
        {'GroupName': name, 'GroupARN': group_arn(name)} for name in groups]}, {})
    for name, tags in groups.items():
        stub.add_response('list_tags_for_resource', {'Tags': [
            {'Key': f'k{index}', 'Value': 'v'} for index in range(tags)]},
            {'ResourceARN': group_arn(name)})


def test_the_group_carrying_the_most_tags_is_measured():
    ctx = context('xray', 'L-E2DD2778')
    with Stubber(ctx.client('xray')) as stub:
        stub_group_tags(stub, {'quiet': 1, 'busy': 3})
        result = check(xray, 'L-E2DD2778')(ctx)
        assert (result['usage'], result['resource_id']) == (3, group_arn('busy'))
        stub.assert_no_pending_responses()


def test_an_untagged_group_counts_as_zero():
    ctx = context('xray', 'L-E2DD2778')
    with Stubber(ctx.client('xray')) as stub:
        stub_group_tags(stub, {'bare': 0})
        result = check(xray, 'L-E2DD2778')(ctx)
        assert (result['usage'], result['resource_id']) == (0, group_arn('bare'))
        stub.assert_no_pending_responses()


def test_a_group_without_an_arn_is_reported():
    ctx = context('xray', 'L-E2DD2778')
    with Stubber(ctx.client('xray')) as stub:
        stub.add_response('get_groups', {'Groups': [{'GroupName': 'nameless'}]}, {})
        with pytest.raises(NoData, match='ARN'):
            check(xray, 'L-E2DD2778')(ctx)


def sampling_rule(name=None):
    """A sampling rule; RuleARN is optional, every field below is required."""
    rule = {'ResourceARN': '*', 'Priority': 1, 'FixedRate': 0.05,
            'ReservoirSize': 1, 'ServiceName': '*', 'ServiceType': '*',
            'Host': '*', 'HTTPMethod': '*', 'URLPath': '*', 'Version': 1}
    if name is not None:
        rule |= {'RuleName': name, 'RuleARN': rule_arn(name)}
    return rule


def stub_rule_tags(stub, rules):
    stub.add_response('get_sampling_rules', {'SamplingRuleRecords': [
        {'SamplingRule': sampling_rule(name)} for name in rules]}, {})
    for name, tags in rules.items():
        stub.add_response('list_tags_for_resource', {'Tags': [
            {'Key': f'k{index}', 'Value': 'v'} for index in range(tags)]},
            {'ResourceARN': rule_arn(name)})


def test_the_sampling_rule_carrying_the_most_tags_is_measured():
    ctx = context('xray', 'L-DB51D338')
    with Stubber(ctx.client('xray')) as stub:
        stub_rule_tags(stub, {'quiet': 1, 'busy': 5})
        result = check(xray, 'L-DB51D338')(ctx)
        assert (result['usage'], result['resource_id']) == (5, rule_arn('busy'))
        stub.assert_no_pending_responses()


def test_a_sampling_rule_record_without_a_rule_is_reported():
    ctx = context('xray', 'L-DB51D338')
    with Stubber(ctx.client('xray')) as stub:
        stub.add_response('get_sampling_rules',
                          {'SamplingRuleRecords': [{'SamplingRule': sampling_rule()}]},
                          {})
        with pytest.raises(NoData, match='ARN'):
            check(xray, 'L-DB51D338')(ctx)
