from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import customer_profiles as profiles
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

DOMAIN = 'retail'
OTHER = 'wholesale'
NOW = datetime(2026, 9, 15, tzinfo=timezone.utc)
TIMESTAMPS = {'CreatedAt': NOW, 'LastUpdatedAt': NOW}
# Each list item shape declares its own required members.
ITEMS = {
    'list_calculated_attribute_definitions': {},
    'list_event_triggers': {},
    'list_recommenders': {},
    'list_recommender_filters': {},
    'list_domain_object_types': {'ObjectTypeName': 'orders'},
    'list_event_streams': {'DomainName': DOMAIN, 'EventStreamName': 'stream',
                           'EventStreamArn': 'arn:aws:profile:eu-central-1:123456789012:stream',
                           'State': 'RUNNING'},
    'list_integrations': dict(DomainName=DOMAIN, Uri='arn:aws:flow', **TIMESTAMPS),
    'list_recommender_schemas': {'RecommenderSchemaName': 'schema', 'Fields': {},
                                 'CreatedAt': NOW, 'Status': 'ACTIVE'},
}


def context(code='L-6603B252'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'profile', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def domain_list(stub, *names):
    stub.add_response('list_domains', {'Items': [
        dict(DomainName=name, **TIMESTAMPS) for name in names]}, {})


def check(code):
    return next(fn for quota, _, fn in profiles.CHECKS if quota == code)


def test_domain_count_deduplicates_paginated_entries():
    ctx = context('L-6603B252')
    with Stubber(ctx.client('customer-profiles')) as stub:
        stub.add_response('list_domains', {'Items': [dict(DomainName=DOMAIN, **TIMESTAMPS)],
                                           'NextToken': 'next'}, {})
        stub.add_response('list_domains', {'Items': [
            dict(DomainName=DOMAIN, **TIMESTAMPS), dict(DomainName=OTHER, **TIMESTAMPS)]},
            {'NextToken': 'next'})
        assert check('L-6603B252')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


class FakeContext:
    """Return a fixed inventory, to reach validation the SDK shapes forbid."""

    def __init__(self, items):
        self.items = items

    def call(self, *args, **kwargs):
        return self.items


def test_a_domain_without_a_name_raises_nodata():
    with pytest.raises(NoData, match='missing its name'):
        profiles.domains(FakeContext([{'CreatedAt': NOW}]))


def test_child_inventories_report_the_largest_domain():
    for code, method, key in (
            ('L-DB27F954', 'list_calculated_attribute_definitions', 'Items'),
            ('L-1DED0840', 'list_event_streams', 'Items'),
            ('L-0A1E1791', 'list_event_triggers', 'Items'),
            ('L-4A5ECB8E', 'list_integrations', 'Items'),
            ('L-B6E9F054', 'list_recommenders', 'Recommenders'),
            ('L-ECB9B0BB', 'list_recommender_schemas', 'RecommenderSchemas'),
            ('L-D53B7246', 'list_recommender_filters', 'RecommenderFilters'),
            ('L-9CF9A111', 'list_domain_object_types', 'Items')):
        ctx = context(code)
        with Stubber(ctx.client('customer-profiles')) as stub:
            domain_list(stub, DOMAIN, OTHER)
            item = ITEMS[method]
            stub.add_response(method, {key: [item]}, {'DomainName': DOMAIN})
            stub.add_response(method, {key: [item] * 3}, {'DomainName': OTHER})
            result = check(code)(ctx)
            assert (result['usage'], result['resource_id']) == (3, OTHER), code
            stub.assert_no_pending_responses()


def test_object_types_are_counted_per_domain():
    ctx = context('L-14092FF4')
    with Stubber(ctx.client('customer-profiles')) as stub:
        domain_list(stub, DOMAIN)
        stub.add_response('list_profile_object_types', {'Items': [
            {'ObjectTypeName': 'orders', 'Description': 'orders'},
            {'ObjectTypeName': 'tickets', 'Description': 'tickets'}]},
            {'DomainName': DOMAIN})
        result = check('L-14092FF4')(ctx)
        assert (result['usage'], result['resource_id']) == (2, DOMAIN)
        stub.assert_no_pending_responses()


def test_keys_are_counted_per_object_type():
    ctx = context('L-A7ED412C')
    with Stubber(ctx.client('customer-profiles')) as stub:
        domain_list(stub, DOMAIN)
        stub.add_response('list_profile_object_types', {'Items': [
            {'ObjectTypeName': 'orders', 'Description': 'orders'},
            {'ObjectTypeName': 'tickets', 'Description': 'tickets'}]},
            {'DomainName': DOMAIN})
        stub.add_response('get_profile_object_type', {
            'ObjectTypeName': 'orders', 'Description': 'orders',
            'Keys': {'_orderId': [{'StandardIdentifiers': ['UNIQUE']}],
                     '_email': [{'StandardIdentifiers': ['PROFILE']}]}},
            {'DomainName': DOMAIN, 'ObjectTypeName': 'orders'})
        # An object type without keys counts as zero rather than failing.
        stub.add_response('get_profile_object_type',
                          {'ObjectTypeName': 'tickets', 'Description': 'tickets'},
                          {'DomainName': DOMAIN, 'ObjectTypeName': 'tickets'})
        result = profiles.keys_per_object_type(ctx)
        assert (result['usage'], result['resource_id']) == (2, f'{DOMAIN}/orders')
        stub.assert_no_pending_responses()


def test_expiration_uses_the_longest_domain_or_object_type_retention():
    ctx = context('L-3217D1F1')
    with Stubber(ctx.client('customer-profiles')) as stub:
        domain_list(stub, DOMAIN)
        stub.add_response('get_domain', dict(DomainName=DOMAIN, DefaultExpirationDays=90,
                                             **TIMESTAMPS), {'DomainName': DOMAIN})
        stub.add_response('list_profile_object_types', {'Items': [
            {'ObjectTypeName': 'orders', 'Description': 'orders'}]},
            {'DomainName': DOMAIN})
        stub.add_response('get_profile_object_type',
                          {'ObjectTypeName': 'orders', 'Description': 'orders',
                           'ExpirationDays': 365},
                          {'DomainName': DOMAIN, 'ObjectTypeName': 'orders'})
        result = profiles.expiration_days(ctx)
        assert (result['usage'], result['resource_id']) == (365, DOMAIN)
        stub.assert_no_pending_responses()


def test_an_account_without_domains_reports_zero():
    ctx = context('L-DB27F954')
    with Stubber(ctx.client('customer-profiles')) as stub:
        stub.add_response('list_domains', {'Items': []}, {})
        result = check('L-DB27F954')(ctx)
        assert (result['usage'], result['resource_id']) == (0, None)
        stub.assert_no_pending_responses()


def test_every_customer_profiles_check_is_registered_for_reporting():
    registered = {code for service, code in custom_keys() if service == 'profile'}
    assert {code for code, _, _ in profiles.CHECKS} <= registered
