import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import wafv2
from modules.qmcore.aws import CheckContext, NoData

ACL = 'arn:aws:wafv2:eu-central-1:123456789012:regional/webacl/one/11111111'
GROUP = 'arn:aws:wafv2:eu-central-1:123456789012:regional/rulegroup/one/22222222'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'wafv2', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in wafv2.CHECKS if candidate == code)


def visibility():
    return {'SampledRequestsEnabled': False, 'CloudWatchMetricsEnabled': False,
            'MetricName': 'metric'}


def rule(name, statement, action=None):
    entry = {'Name': name, 'Priority': 1, 'Statement': statement,
             'VisibilityConfig': visibility()}
    if action:
        entry['Action'] = action
    return entry


def byte_match(search='admin', transformations=1):
    return {'ByteMatchStatement': {
        'SearchString': search.encode('utf-8'),
        'FieldToMatch': {'UriPath': {}},
        'TextTransformations': [{'Priority': index, 'Type': 'NONE'}
                                for index in range(transformations)],
        'PositionalConstraint': 'CONTAINS'}}


def rate_based(scope_down=None):
    statement = {'Limit': 1000, 'AggregateKeyType': 'IP'}
    if scope_down:
        statement['ScopeDownStatement'] = scope_down
    return {'RateBasedStatement': statement}


def web_acl(rules, bodies=None, domains=None):
    acl = {'Name': 'one', 'Id': '11111111', 'ARN': ACL, 'Capacity': 700,
           'DefaultAction': {'Allow': {}}, 'VisibilityConfig': visibility(),
           'Rules': rules}
    if bodies:
        acl['CustomResponseBodies'] = bodies
    if domains:
        acl['TokenDomains'] = domains
    return acl


def stub_web_acl(stub, acl):
    stub.add_response('list_web_acls', {'WebACLs': [
        {'Name': acl['Name'], 'Id': acl['Id'], 'ARN': acl['ARN']}]},
        {'Scope': 'REGIONAL'})
    stub.add_response('get_web_acl', {'WebACL': acl},
                      {'Scope': 'REGIONAL', 'Id': acl['Id'], 'Name': acl['Name']})


def stub_rule_groups(stub, groups=()):
    stub.add_response('list_rule_groups', {'RuleGroups': [
        {'Name': group['Name'], 'Id': group['Id'], 'ARN': group['ARN']}
        for group in groups]}, {'Scope': 'REGIONAL'})
    for group in groups:
        stub.add_response('get_rule_group', {'RuleGroup': group},
                          {'Scope': 'REGIONAL', 'Id': group['Id'],
                           'Name': group['Name']})


def test_nested_rate_based_statements_are_counted():
    ctx = context('L-B1635397')
    nested = {'AndStatement': {'Statements': [byte_match(), rate_based()]}}
    acl = web_acl([rule('outer', rate_based(scope_down=byte_match())),
                   rule('nested', nested)])
    with Stubber(ctx.client('wafv2')) as stub:
        stub_web_acl(stub, acl)
        result = check('L-B1635397')(ctx)
        assert (result['usage'], result['resource_id']) == (2, ACL)
        stub.assert_no_pending_responses()


def test_capacity_and_token_domains_come_from_the_full_web_acl():
    ctx = context('L-D9F31E8A')
    acl = web_acl([rule('one', byte_match())], domains=['example.com', 'example.org'])
    with Stubber(ctx.client('wafv2')) as stub:
        stub_web_acl(stub, acl)
        assert check('L-D9F31E8A')(ctx)['usage'] == 700
        assert check('L-11D00F38')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_response_bodies_are_counted_and_measured_in_kilobytes():
    ctx = context('L-71C2E81B')
    bodies = {'small': {'ContentType': 'TEXT_PLAIN', 'Content': 'a' * 512},
              'large': {'ContentType': 'TEXT_PLAIN', 'Content': 'b' * 2048}}
    acl = web_acl([rule('one', byte_match())], bodies=bodies)
    with Stubber(ctx.client('wafv2')) as stub:
        stub_web_acl(stub, acl)
        stub_rule_groups(stub)
        assert check('L-71C2E81B')(ctx)['usage'] == 2
        assert check('L-6F32B880')(ctx)['usage'] == pytest.approx(2.5)
        largest = check('L-0A8A309C')(ctx)
        assert (largest['usage'], largest['resource_id']) == (2.0, f'{ACL}#large')
        stub.assert_no_pending_responses()


def test_custom_headers_are_counted_per_definition_and_per_resource():
    ctx = context('L-2D9CB303')
    block = rule('one', byte_match(), action={'Block': {'CustomResponse': {
        'ResponseCode': 403, 'ResponseHeaders': [
            {'Name': 'x-one', 'Value': '1'}, {'Name': 'x-two', 'Value': '2'}]}}})
    allow = rule('two', byte_match(), action={'Allow': {'CustomRequestHandling': {
        'InsertHeaders': [{'Name': 'x-three', 'Value': '3'}]}}})
    acl = web_acl([block, allow])
    with Stubber(ctx.client('wafv2')) as stub:
        stub_web_acl(stub, acl)
        stub_rule_groups(stub)
        assert check('L-2D9CB303')(ctx)['usage'] == 1
        assert check('L-E4E414A8')(ctx)['usage'] == 2
        assert check('L-45C90A8A')(ctx)['usage'] == 2
        assert check('L-CCCD1D7B')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_search_strings_and_transformations_are_measured_per_statement():
    ctx = context('L-5E8DF1EF')
    acl = web_acl([rule('one', byte_match('admin', transformations=3)),
                   rule('two', byte_match('administrator', transformations=1))])
    with Stubber(ctx.client('wafv2')) as stub:
        stub_web_acl(stub, acl)
        stub_rule_groups(stub)
        assert check('L-5E8DF1EF')(ctx)['usage'] == len('administrator')
        assert check('L-041DD6D3')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_a_mismatched_web_acl_identity_raises_nodata():
    ctx = context('L-D9F31E8A')
    acl = web_acl([rule('one', byte_match())])
    with Stubber(ctx.client('wafv2')) as stub:
        stub.add_response('list_web_acls', {'WebACLs': [
            {'Name': 'one', 'Id': '11111111', 'ARN': ACL}]}, {'Scope': 'REGIONAL'})
        stub.add_response('get_web_acl', {'WebACL': {**acl, 'Id': '99999999'}},
                          {'Scope': 'REGIONAL', 'Id': '11111111', 'Name': 'one'})
        with pytest.raises(NoData, match='does not match the requested identity'):
            check('L-D9F31E8A')(ctx)
