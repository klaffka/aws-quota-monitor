"""Every check below once read a response key the API does not return.

A wrong key makes ``paginate`` yield an empty list, so the check reports
``usage=0`` with status OK: a fabricated zero that looks like a measurement.
These tests stub the real client, so only the documented key satisfies them.
"""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import entityresolution, guardduty, lakeformation, rds_resources, redshift, sitewise
from modules.qmcore.aws import CheckContext


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_guardduty_trusted_ip_sets_read_ip_set_ids():
    ctx = context('guardduty', 'L-AFBA2260')
    with Stubber(ctx.client('guardduty')) as stub:
        stub.add_response('list_detectors', {'DetectorIds': ['detector-a']}, {})
        stub.add_response('list_ip_sets', {'IpSetIds': ['set-1', 'set-2']},
                          {'DetectorId': 'detector-a'})
        result = check(guardduty, 'L-AFBA2260')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'detector-a')
        stub.assert_no_pending_responses()


def test_guardduty_threat_intel_sets_read_threat_intel_set_ids():
    ctx = context('guardduty', 'L-2C0E14B9')
    with Stubber(ctx.client('guardduty')) as stub:
        stub.add_response('list_detectors', {'DetectorIds': ['detector-a']}, {})
        stub.add_response('list_threat_intel_sets', {'ThreatIntelSetIds': ['set-1']},
                          {'DetectorId': 'detector-a'})
        assert check(guardduty, 'L-2C0E14B9')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


MOMENT = datetime(2026, 9, 15, tzinfo=UTC)
STAMPS = {'createdAt': MOMENT, 'updatedAt': MOMENT}


@pytest.mark.parametrize('code, method, key, item', [
    ('L-60DAF647', 'list_matching_workflows', 'workflowSummaries',
     {'workflowName': 'a', 'workflowArn': 'arn:a', 'resolutionType': 'RULE_MATCHING', **STAMPS}),
    ('L-C5A3094C', 'list_id_mapping_workflows', 'workflowSummaries',
     {'workflowName': 'a', 'workflowArn': 'arn:a', **STAMPS}),
    ('L-FBA1B7BB', 'list_id_namespaces', 'idNamespaceSummaries',
     {'idNamespaceName': 'a', 'idNamespaceArn': 'arn:a', 'type': 'SOURCE', **STAMPS}),
    ('L-00E43259', 'list_schema_mappings', 'schemaList',
     {'schemaName': 'a', 'schemaArn': 'arn:a', 'hasWorkflows': False, **STAMPS}),
])
def test_entity_resolution_checks_read_the_documented_summary_keys(code, method, key, item):
    ctx = context('entityresolution', code)
    with Stubber(ctx.client('entityresolution')) as stub:
        stub.add_response(method, {key: [item]}, {})
        assert check(entityresolution, code)(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_lakeformation_tags_read_lf_tags():
    ctx = context('lakeformation', 'L-F165AF61')
    with Stubber(ctx.client('lakeformation')) as stub:
        stub.add_response('list_lf_tags', {'LFTags': [{'TagKey': 'one', 'TagValues': ['a']}]}, {})
        assert check(lakeformation, 'L-F165AF61')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, method, response', [
    ('L-9FA33840', 'describe_option_groups', {'OptionGroupsList': [{'OptionGroupName': 'one'}]}),
    ('L-A59F4C87', 'describe_event_subscriptions', {'EventSubscriptionsList': [{'CustSubscriptionId': 'one'}]}),
])
def test_rds_checks_read_the_list_suffixed_keys(code, method, response):
    ctx = context('rds', code)
    with Stubber(ctx.client('rds')) as stub:
        stub.add_response(method, response, {})
        assert check(rds_resources, code)(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_redshift_parameter_groups_read_parameter_groups():
    ctx = context('redshift', 'L-A3830BB3')
    with Stubber(ctx.client('redshift')) as stub:
        stub.add_response('describe_cluster_parameter_groups',
                          {'ParameterGroups': [{'ParameterGroupName': 'one'}]}, {})
        assert check(redshift, 'L-A3830BB3')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_sitewise_gateways_read_gateway_summaries():
    ctx = context('iotsitewise', 'L-179151C6')
    with Stubber(ctx.client('iotsitewise')) as stub:
        gateway = {'gatewayId': 'g' * 36, 'gatewayName': 'one',
                   'creationDate': MOMENT, 'lastUpdateDate': MOMENT}
        stub.add_response('list_gateways', {'gatewaySummaries': [gateway]}, {})
        assert check(sitewise, 'L-179151C6')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()
