from datetime import datetime, UTC

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import iot, iotcore
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

NOW = datetime(2026, 9, 15, tzinfo=UTC)
PROFILE = 'anomalies'
GROUP = 'factory'
STREAM = 'firmware'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012', now=NOW)


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_running_jobs_are_filtered_server_side_by_status_and_selection():
    for code, arguments in (
            ('L-FBF5CD89', {'status': 'IN_PROGRESS'}),
            ('L-4E068A30', {'status': 'IN_PROGRESS', 'targetSelection': 'CONTINUOUS'}),
            ('L-D80B05DB', {'status': 'IN_PROGRESS', 'targetSelection': 'SNAPSHOT'})):
        ctx = context('iot', code)
        with Stubber(ctx.client('iot')) as stub:
            stub.add_response('list_jobs', {'jobs': [
                {'jobId': 'a', 'status': 'IN_PROGRESS'},
                {'jobId': 'b', 'status': 'IN_PROGRESS'}]}, arguments)
            assert check(iot, code)(ctx)['usage'] == 2, code
            stub.assert_no_pending_responses()


def test_behaviors_and_targets_are_reported_per_security_profile():
    ctx = context('iot', 'L-2F1C9734')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_security_profiles', {'securityProfileIdentifiers': [
            {'name': PROFILE, 'arn': f'arn:aws:iot:::securityprofile/{PROFILE}'}]}, {})
        stub.add_response('describe_security_profile', {
            'securityProfileName': PROFILE,
            'behaviors': [{'name': 'b1'}, {'name': 'b2'}, {'name': 'b3'}]},
            {'securityProfileName': PROFILE})
        result = iot.behaviors_per_security_profile(ctx)
        assert (result['usage'], result['resource_id']) == (3, PROFILE)
        stub.assert_no_pending_responses()


def test_security_profiles_are_inverted_onto_their_targets():
    target = 'arn:aws:iot:eu-central-1:123456789012:all/things'
    ctx = context('iot', 'L-FF03CD81')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_security_profiles', {'securityProfileIdentifiers': [
            {'name': PROFILE, 'arn': f'arn:aws:iot:::securityprofile/{PROFILE}'},
            {'name': 'other', 'arn': 'arn:aws:iot:::securityprofile/other'}]}, {})
        for name in (PROFILE, 'other'):
            stub.add_response('list_targets_for_security_profile', {
                'securityProfileTargets': [{'arn': target}]},
                {'securityProfileName': name})
        result = iot.security_profiles_per_target(ctx)
        assert (result['usage'], result['resource_id']) == (2, target)
        stub.assert_no_pending_responses()


def test_files_are_counted_per_stream():
    ctx = context('iot', 'L-D32D434B')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_streams', {'streams': [{'streamId': STREAM}]}, {})
        stub.add_response('describe_stream', {'streamInfo': {
            'streamId': STREAM, 'files': [{'fileId': 1}, {'fileId': 2}]}},
            {'streamId': STREAM})
        result = iot.files_per_stream(ctx)
        assert (result['usage'], result['resource_id']) == (2, STREAM)
        stub.assert_no_pending_responses()


def test_on_demand_audits_ask_for_a_bounded_window():
    ctx = context('iot', 'L-1EF777B4')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_audit_tasks', {'tasks': [
            {'taskId': 't1', 'taskStatus': 'IN_PROGRESS',
             'taskType': 'ON_DEMAND_AUDIT_TASK'}]},
            {'startTime': NOW - iot.AUDIT_WINDOW, 'endTime': NOW,
             'taskStatus': 'IN_PROGRESS', 'taskType': 'ON_DEMAND_AUDIT_TASK'})
        assert iot.on_demand_audits_in_progress(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_actions_are_counted_per_topic_rule():
    ctx = context('iotcore', 'L-51309716')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_topic_rules', {'rules': [{'ruleName': 'route'}]}, {})
        stub.add_response('get_topic_rule', {'rule': {
            'ruleName': 'route', 'sql': 'SELECT * FROM "a"', 'actions': [
                {'republish': {'roleArn': 'arn:aws:iam::123456789012:role/r',
                               'topic': 'b'}},
                {'lambda': {'functionArn':
                            'arn:aws:lambda:eu-central-1:123456789012:function:f'}}]}},
            {'ruleName': 'route'})
        result = iotcore.actions_per_topic_rule(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'route')
        stub.assert_no_pending_responses()


def test_thing_group_depth_uses_the_ancestors_the_group_reports():
    ctx = context('iotcore', 'L-1AC7411F')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_groups', {'thingGroups': [
            {'groupName': GROUP, 'groupArn': f'arn:aws:iot:::thinggroup/{GROUP}'}]}, {})
        stub.add_response('describe_thing_group', {
            'thingGroupName': GROUP,
            'thingGroupMetadata': {'rootToParentThingGroups': [
                {'groupName': 'root'}, {'groupName': 'site'}]}},
            {'thingGroupName': GROUP})
        result = iotcore.thing_group_hierarchy_depth(ctx)
        # Two ancestors plus the group itself.
        assert (result['usage'], result['resource_id']) == (3, GROUP)
        stub.assert_no_pending_responses()


def test_direct_child_groups_ask_for_a_non_recursive_listing():
    ctx = context('iotcore', 'L-9D744041')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_groups', {'thingGroups': [
            {'groupName': GROUP}]}, {})
        stub.add_response('list_thing_groups', {'thingGroups': [
            {'groupName': 'line-1'}, {'groupName': 'line-2'}]},
            {'parentGroup': GROUP, 'recursive': False})
        result = iotcore.direct_child_groups(ctx)
        assert (result['usage'], result['resource_id']) == (2, GROUP)
        stub.assert_no_pending_responses()


def test_a_thing_group_without_a_name_raises_nodata():
    ctx = context('iotcore', 'L-9D744041')
    with Stubber(ctx.client('iot')) as stub:
        stub.add_response('list_thing_groups', {'thingGroups': [{'groupArn': 'a'}]}, {})
        with pytest.raises(NoData, match='missing its name'):
            iotcore.thing_groups(ctx)


def test_every_new_iot_check_is_registered_for_reporting():
    for module, service in ((iot, 'iot'), (iotcore, 'iotcore')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
