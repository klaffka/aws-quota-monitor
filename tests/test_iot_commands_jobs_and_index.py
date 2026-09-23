"""IoT command, job, security profile and fleet index quotas."""
from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iot, iotcore
from modules.qmcore.aws import CheckContext, NoData

MOMENT = datetime(2026, 9, 16, tzinfo=UTC)


def context(code, service='iot'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(code, checks):
    return next(fn for quota, _name, fn in checks if quota == code)


def behavior(name, **value):
    return {'name': name, 'metric': 'aws:num-messages-received',
            'criteria': {'comparisonOperator': 'less-than', 'value': value}}


def test_the_largest_behaviour_value_list_decides_the_element_count():
    """One behaviour's value list is what the quota bounds, not the profile."""
    ctx = context('L-971FA845')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_security_profiles', {'securityProfileIdentifiers': [
            {'name': 'small', 'arn': 'arn:sp/small'},
            {'name': 'large', 'arn': 'arn:sp/large'}]}, {})
        stub.add_response('describe_security_profile', {
            'securityProfileName': 'small',
            'behaviors': [behavior('a', ports=[1, 2])]}, {'securityProfileName': 'small'})
        stub.add_response('describe_security_profile', {
            'securityProfileName': 'large',
            'behaviors': [behavior('b', cidrs=['10.0.0.0/8']),
                          behavior('c', strings=['x', 'y', 'z'])]},
            {'securityProfileName': 'large'})
        result = check('L-971FA845', iot.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'large/c')
        stub.assert_no_pending_responses()


def test_a_behaviour_without_a_value_counts_as_zero():
    """A machine-learning behaviour carries no threshold list at all."""
    ctx = context('L-971FA845')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_security_profiles', {'securityProfileIdentifiers': [
            {'name': 'ml', 'arn': 'arn:sp/ml'}]}, {})
        stub.add_response('describe_security_profile', {
            'securityProfileName': 'ml',
            'behaviors': [{'name': 'b', 'metric': 'aws:num-messages-received'}]},
            {'securityProfileName': 'ml'})
        assert check('L-971FA845', iot.CHECKS)(ctx)['usage'] == 0


def test_the_job_with_the_most_targets_decides_the_count():
    ctx = context('L-9D1E0A0D')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_jobs', {'jobs': [
            {'jobId': 'one', 'status': 'IN_PROGRESS'},
            {'jobId': 'two', 'status': 'COMPLETED'}]}, {})
        stub.add_response('describe_job', {'job': {
            'jobId': 'one', 'targets': ['arn:thing/a']}}, {'jobId': 'one'})
        stub.add_response('describe_job', {'job': {
            'jobId': 'two', 'targets': ['arn:thing/a', 'arn:thing/b']}}, {'jobId': 'two'})
        result = check('L-9D1E0A0D', iot.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'two')
        stub.assert_no_pending_responses()


def test_a_job_detail_for_a_different_job_is_reported():
    ctx = context('L-9D1E0A0D')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_jobs', {'jobs': [{'jobId': 'one', 'status': 'IN_PROGRESS'}]}, {})
        stub.add_response('describe_job', {'job': {'jobId': 'other',
                                                   'targets': ['arn:thing/a']}},
                          {'jobId': 'one'})
        with pytest.raises(NoData, match='identity'):
            check('L-9D1E0A0D', iot.CHECKS)(ctx)


@pytest.mark.parametrize('code, expected', [('L-57F7D467', 2), ('L-7068DC7F', 1)])
def test_both_fleet_index_filters_come_from_one_configuration(code, expected):
    ctx = context(code)
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('get_indexing_configuration', {'thingIndexingConfiguration': {
            'thingIndexingMode': 'REGISTRY_AND_SHADOW',
            'filter': {'namedShadowNames': ['one', 'two'],
                       'geoLocations': [{'name': 'here', 'order': 'LatLon'}]}}}, {})
        result = check(code, iot.CHECKS)(ctx)
        assert (result['usage'], result['method']) == (expected, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_an_unconfigured_fleet_index_filter_counts_as_zero():
    """GetIndexingConfiguration answers whether or not indexing is enabled."""
    ctx = context('L-57F7D467')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('get_indexing_configuration', {'thingIndexingConfiguration': {
            'thingIndexingMode': 'OFF'}}, {})
        assert check('L-57F7D467', iot.CHECKS)(ctx)['usage'] == 0


def test_the_command_with_the_most_mandatory_parameters_decides_the_count():
    ctx = context('L-F570A784')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_commands', {'commands': [
            {'commandId': 'one', 'commandArn': 'arn:cmd/one'},
            {'commandId': 'two', 'commandArn': 'arn:cmd/two'}]}, {})
        stub.add_response('get_command', {
            'commandId': 'one', 'commandArn': 'arn:cmd/one',
            'mandatoryParameters': [{'name': 'a'}]}, {'commandId': 'one'})
        stub.add_response('get_command', {
            'commandId': 'two', 'commandArn': 'arn:cmd/two',
            'mandatoryParameters': [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]},
            {'commandId': 'two'})
        result = check('L-F570A784', iot.CHECKS)(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'two')
        stub.assert_no_pending_responses()


def test_only_unfinished_command_executions_count_towards_concurrency():
    """IoT lists executions only per command, and then without a status filter."""
    ctx = context('L-631C84B3')
    since = {'after': '1970-01-01T00:00'}
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_commands', {'commands': [
            {'commandId': 'one', 'commandArn': 'arn:cmd/one'},
            {'commandId': 'two', 'commandArn': 'arn:cmd/two'}]}, {})
        stub.add_response('list_command_executions', {'commandExecutions': [
            {'executionId': 'e1', 'status': 'CREATED'},
            {'executionId': 'e2', 'status': 'SUCCEEDED'}]},
            {'commandArn': 'arn:cmd/one', 'startedTimeFilter': since})
        stub.add_response('list_command_executions', {'commandExecutions': [
            {'executionId': 'e3', 'status': 'IN_PROGRESS'},
            {'executionId': 'e4', 'status': 'IN_PROGRESS'},
            {'executionId': 'e5', 'status': 'TIMED_OUT'}]},
            {'commandArn': 'arn:cmd/two', 'startedTimeFilter': since})
        result = check('L-631C84B3', iot.CHECKS)(ctx)
        assert (result['usage'], result['method']) == (3, 'ACCOUNT_COUNT')
        stub.assert_no_pending_responses()


def test_a_command_execution_without_status_is_no_data():
    ctx = context('L-631C84B3')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_commands', {'commands': [
            {'commandId': 'one', 'commandArn': 'arn:cmd/one'}]}, {})
        stub.add_response('list_command_executions', {'commandExecutions': [
            {'executionId': 'e1'}]},
            {'commandArn': 'arn:cmd/one', 'startedTimeFilter': {'after': '1970-01-01T00:00'}})
        with pytest.raises(NoData):
            check('L-631C84B3', iot.CHECKS)(ctx)


def test_the_iot_core_dynamic_group_code_reuses_the_same_measurement():
    """Both service codes name the same quota over the same inventory."""
    assert (check('L-6EC13FE5', iotcore.CHECKS)
            is check('L-2F036C7C', iot.CHECKS))
