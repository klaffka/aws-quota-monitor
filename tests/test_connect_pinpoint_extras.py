import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import connect, pinpoint
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

APP = '11111111111111111111111111111111'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'pinpoint', 'QuotaCode': code, 'Value': 50}],
                        account='123456789012')


def check(code):
    return next(fn for quota, _, fn in pinpoint.CHECKS if quota == code)


def apps(stub):
    stub.add_response('get_apps', {'ApplicationsResponse': {'Item': [
        {'Id': APP, 'Arn': 'arn:aws:mobiletargeting:::apps/a', 'Name': 'app'}]}}, {})


def test_only_unfinished_import_jobs_are_concurrent():
    ctx = context('L-4BC0A2FD')
    with Stubber(ctx.client('pinpoint')) as stub:
        apps(stub)
        stub.add_response('get_import_jobs', {'ImportJobsResponse': {'Item': [
            {'ApplicationId': APP, 'Id': 'j1', 'JobStatus': 'PROCESSING',
             'CreationDate': '2026-09-15', 'Definition': {'S3Url': 's3://a/b',
                                                          'RoleArn': 'arn:aws:iam::1:role/r',
                                                          'Format': 'CSV'},
             'Type': 'IMPORT'},
            {'ApplicationId': APP, 'Id': 'j2', 'JobStatus': 'COMPLETED',
             'CreationDate': '2026-09-15', 'Definition': {'S3Url': 's3://a/c',
                                                          'RoleArn': 'arn:aws:iam::1:role/r',
                                                          'Format': 'CSV'},
             'Type': 'IMPORT'}]}}, {'ApplicationId': APP})
        assert pinpoint.concurrent_import_jobs(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_an_unknown_import_job_status_raises_nodata():
    ctx = context('L-4BC0A2FD')
    with Stubber(ctx.client('pinpoint')) as stub:
        apps(stub)
        stub.add_response('get_import_jobs', {'ImportJobsResponse': {'Item': [
            {'ApplicationId': APP, 'Id': 'j1', 'JobStatus': 'DAWDLING',
             'CreationDate': '2026-09-15', 'Definition': {'S3Url': 's3://a/b',
                                                          'RoleArn': 'arn:aws:iam::1:role/r',
                                                          'Format': 'CSV'},
             'Type': 'IMPORT'}]}}, {'ApplicationId': APP})
        with pytest.raises(NoData, match='unknown status'):
            pinpoint.concurrent_import_jobs(ctx)


def test_event_based_campaigns_are_recognised_by_their_schedule_filter():
    ctx = context('L-CC53764D')
    with Stubber(ctx.client('pinpoint')) as stub:
        apps(stub)
        stub.add_response('get_campaigns', {'CampaignsResponse': {'Item': [
            {'ApplicationId': APP, 'Id': 'c1', 'Arn': 'a', 'CreationDate': 'd',
             'LastModifiedDate': 'd', 'SegmentId': 's', 'SegmentVersion': 1,
             'Schedule': {'StartTime': 'IMMEDIATE',
                          'EventFilter': {'Dimensions': {}, 'FilterType': 'ENDPOINT'}}},
            {'ApplicationId': APP, 'Id': 'c2', 'Arn': 'b', 'CreationDate': 'd',
             'LastModifiedDate': 'd', 'SegmentId': 's', 'SegmentVersion': 1,
             'Schedule': {'StartTime': 'IMMEDIATE'}}]}}, {'ApplicationId': APP})
        assert pinpoint.event_based_campaigns(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def journey(identity, state, activities=0, event_start=False):
    result = {'ApplicationId': APP, 'Id': identity, 'Name': identity, 'State': state,
              'Activities': {f'a{index}': {} for index in range(activities)}}
    if event_start:
        result['StartCondition'] = {'EventStartCondition': {
            'EventFilter': {'Dimensions': {}, 'FilterType': 'ENDPOINT'}}}
    return result


def test_active_event_triggered_journeys_need_both_conditions():
    ctx = context('L-692A3DD2')
    with Stubber(ctx.client('pinpoint')) as stub:
        apps(stub)
        stub.add_response('list_journeys', {'JourneysResponse': {'Item': [
            journey('j1', 'ACTIVE', event_start=True),
            journey('j2', 'ACTIVE'),
            journey('j3', 'DRAFT', event_start=True)]}}, {'ApplicationId': APP})
        assert pinpoint.active_event_triggered_journeys(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_activities_are_counted_per_journey():
    ctx = context('L-08122D1D')
    with Stubber(ctx.client('pinpoint')) as stub:
        apps(stub)
        stub.add_response('list_journeys', {'JourneysResponse': {'Item': [
            journey('j1', 'ACTIVE', activities=2),
            journey('j2', 'ACTIVE', activities=5)]}}, {'ApplicationId': APP})
        result = pinpoint.activities_per_journey(ctx)
        assert (result['usage'], result['resource_id']) == (5, 'j2')
        stub.assert_no_pending_responses()


def test_the_new_connect_and_pinpoint_checks_are_registered():
    for module, service in ((pinpoint, 'pinpoint'), (connect, 'connect')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service


CONNECT_ARN = 'arn:aws:connect:eu-central-1:123456789012:instance/first'


def connect_context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'connect', 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def connect_check(code):
    return next(fn for candidate, _, fn in connect.CHECKS if candidate == code)


def instance(stub, quotas, code):
    stub.add_response('list_instances',
                      {'InstanceSummaryList': [{'Id': 'first', 'Arn': CONNECT_ARN}]}, {})
    quotas.add_response('get_service_quota', {'Quota': {
        'ServiceCode': 'connect', 'QuotaCode': code, 'Value': 100,
        'QuotaContext': {'ContextId': CONNECT_ARN, 'ContextScope': 'RESOURCE',
                         'ContextScopeType': 'AWS::Connect::Instance'}}},
        {'ServiceCode': 'connect', 'QuotaCode': code, 'ContextId': CONNECT_ARN})


def test_agent_statuses_are_counted_per_instance():
    ctx = connect_context('L-D945C9A8')
    with Stubber(ctx.client('connect')) as stub, \
            Stubber(ctx.client('service-quotas')) as quotas:
        instance(stub, quotas, 'L-D945C9A8')
        stub.add_response('list_agent_statuses', {'AgentStatusSummaryList': [
            {'Id': 'a', 'Name': 'Available', 'Type': 'ROUTABLE'},
            {'Id': 'b', 'Name': 'Lunch', 'Type': 'CUSTOM'}]}, {'InstanceId': 'first'})
        assert connect_check('L-D945C9A8')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def value(record):
    return {'RecordId': record, 'AttributeName': 'name', 'ValueType': 'TEXT',
            'Value': record, 'PrimaryValues': []}


def test_data_table_values_report_the_fullest_table():
    ctx = connect_context('L-735CD262')
    with Stubber(ctx.client('connect')) as stub, \
            Stubber(ctx.client('service-quotas')) as quotas:
        instance(stub, quotas, 'L-735CD262')
        stub.add_response('list_data_tables', {'DataTableSummaryList': [
            {'Id': 'table-a', 'Name': 'a'}, {'Id': 'table-b', 'Name': 'b'}]},
            {'InstanceId': 'first'})
        stub.add_response('list_data_table_values', {'Values': [value('r1')]},
                          {'InstanceId': 'first', 'DataTableId': 'table-a'})
        stub.add_response('list_data_table_values',
                          {'Values': [value('r1'), value('r2'), value('r3')]},
                          {'InstanceId': 'first', 'DataTableId': 'table-b'})
        result = connect_check('L-735CD262')(ctx)
        assert (result['usage'], result['meta']['childResourceId']) == (3, 'table-b')
        stub.assert_no_pending_responses()


def test_queue_email_addresses_report_the_fullest_queue():
    ctx = connect_context('L-7B867368')
    with Stubber(ctx.client('connect')) as stub, \
            Stubber(ctx.client('service-quotas')) as quotas:
        instance(stub, quotas, 'L-7B867368')
        stub.add_response('list_queues', {'QueueSummaryList': [
            {'Id': 'queue-a', 'Name': 'a'}, {'Id': 'queue-b', 'Name': 'b'}]},
            {'InstanceId': 'first'})
        stub.add_response('list_queue_email_addresses', {'EmailAddressMetadataList': [
            {'Id': 'mail-1'}, {'Id': 'mail-2'}]},
            {'InstanceId': 'first', 'QueueId': 'queue-a'})
        stub.add_response('list_queue_email_addresses',
                          {'EmailAddressMetadataList': [{'Id': 'mail-3'}]},
                          {'InstanceId': 'first', 'QueueId': 'queue-b'})
        result = connect_check('L-7B867368')(ctx)
        assert (result['usage'], result['meta']['childResourceId']) == (2, 'queue-a')
        stub.assert_no_pending_responses()
