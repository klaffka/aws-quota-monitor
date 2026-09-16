import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import waf_regional
from modules.qmcore.aws import CheckContext, NoData

ACL = '11111111-1111-1111-1111-111111111111'
SET = '22222222-2222-2222-2222-222222222222'
OTHER = '33333333-3333-3333-3333-333333333333'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'waf-regional', 'QuotaCode': code,
                          'Value': 100}], account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in waf_regional.CHECKS if candidate == code)


def test_condition_filters_are_reported_for_the_fullest_set():
    ctx = context('L-954F3F3A')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub.add_response('list_sql_injection_match_sets', {
            'SqlInjectionMatchSets': [
                {'SqlInjectionMatchSetId': SET, 'Name': 'one'},
                {'SqlInjectionMatchSetId': OTHER, 'Name': 'two'}]}, {})
        stub.add_response('get_sql_injection_match_set', {
            'SqlInjectionMatchSet': {
                'SqlInjectionMatchSetId': SET, 'Name': 'one',
                'SqlInjectionMatchTuples': [
                    {'FieldToMatch': {'Type': 'URI'}, 'TextTransformation': 'NONE'},
                    {'FieldToMatch': {'Type': 'BODY'}, 'TextTransformation': 'NONE'}]}},
            {'SqlInjectionMatchSetId': SET})
        stub.add_response('get_sql_injection_match_set', {
            'SqlInjectionMatchSet': {
                'SqlInjectionMatchSetId': OTHER, 'Name': 'two',
                'SqlInjectionMatchTuples': []}}, {'SqlInjectionMatchSetId': OTHER})
        result = check('L-954F3F3A')(ctx)
        assert (result['usage'], result['resource_id']) == (2, SET)
        stub.assert_no_pending_responses()


def test_a_condition_detail_for_another_identity_raises_nodata():
    ctx = context('L-AF52C91B')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub.add_response('list_ip_sets',
                          {'IPSets': [{'IPSetId': SET, 'Name': 'one'}]}, {})
        stub.add_response('get_ip_set', {'IPSet': {
            'IPSetId': OTHER, 'Name': 'other', 'IPSetDescriptors': []}},
            {'IPSetId': SET})
        with pytest.raises(NoData, match='different identity'):
            check('L-AF52C91B')(ctx)


def test_geo_locations_are_counted_per_set():
    ctx = context('L-FFB853E8')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub.add_response('list_geo_match_sets', {'GeoMatchSets': [
            {'GeoMatchSetId': SET, 'Name': 'one'}]}, {})
        stub.add_response('get_geo_match_set', {'GeoMatchSet': {
            'GeoMatchSetId': SET, 'Name': 'one', 'GeoMatchConstraints': [
                {'Type': 'Country', 'Value': 'DE'},
                {'Type': 'Country', 'Value': 'FR'}]}}, {'GeoMatchSetId': SET})
        result = check('L-FFB853E8')(ctx)
        assert (result['usage'], result['resource_id']) == (2, SET)
        stub.assert_no_pending_responses()


def test_logging_destinations_are_counted_per_web_acl():
    ctx = context('L-0043356F')
    arn = f'arn:aws:waf-regional:eu-central-1:123456789012:webacl/{ACL}'
    with Stubber(ctx.client('waf-regional')) as stub:
        stub.add_response('list_logging_configurations', {
            'LoggingConfigurations': [
                {'ResourceArn': arn,
                 'LogDestinationConfigs': ['arn:aws:firehose:::one',
                                           'arn:aws:firehose:::two']}]}, {})
        result = check('L-0043356F')(ctx)
        assert (result['usage'], result['resource_id']) == (2, arn)
        stub.assert_no_pending_responses()


def test_the_plain_inventories_count_their_listings():
    ctx = context('L-7BF8015E')
    with Stubber(ctx.client('waf-regional')) as stub:
        stub.add_response('list_rules', {'Rules': [
            {'RuleId': SET, 'Name': 'one'}, {'RuleId': OTHER, 'Name': 'two'}]}, {})
        assert check('L-7BF8015E')(ctx)['usage'] == 2
        stub.add_response('list_rate_based_rules',
                          {'Rules': [{'RuleId': SET, 'Name': 'one'}]}, {})
        assert check('L-6DA23DDF')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
