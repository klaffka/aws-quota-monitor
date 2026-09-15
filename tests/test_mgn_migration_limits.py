import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import mgn
from modules.qmcore.aws import CheckContext, NoData

SERVER = 's-11111111111111111'
OTHER = 's-22222222222222222'
TEMPLATE = 'lct-33333333333333333'


def context(code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'mgn', 'QuotaCode': code, 'Value': 200}],
                        account='123456789012')


def check(code):
    return next(fn for candidate, _, fn in mgn.CHECKS if candidate == code)


def server(identity, application=None):
    entry = {'sourceServerID': identity, 'isArchived': False}
    if application:
        entry['applicationID'] = application
    return entry


def test_source_servers_are_counted_whole_and_grouped_by_application():
    ctx = context('L-967C958D')
    with Stubber(ctx.client('mgn')) as stub:
        stub.add_response('describe_source_servers', {'items': [
            server(SERVER, 'app-111111111111111111'), server(OTHER, 'app-111111111111111111'),
            {'sourceServerID': 's-33333333333333333', 'isArchived': True}]}, {})
        assert check('L-967C958D')(ctx)['usage'] == 3
        assert check('L-50980698')(ctx)['usage'] == 2
        grouped = check('L-90A3F9F5')(ctx)
        assert (grouped['usage'], grouped['resource_id']) == (2, 'app-111111111111111111')
        stub.assert_no_pending_responses()


def test_a_source_server_without_an_archive_flag_raises_nodata():
    ctx = context('L-50980698')
    with Stubber(ctx.client('mgn')) as stub:
        stub.add_response('describe_source_servers',
                          {'items': [{'sourceServerID': SERVER}]}, {})
        with pytest.raises(NoData, match='archive flag'):
            check('L-50980698')(ctx)


def job(identity, status, servers):
    return {'jobID': identity, 'status': status,
            'participatingServers': [{'sourceServerID': s} for s in servers]}


def test_completed_jobs_release_their_servers():
    ctx = context('L-FE2EBE17')
    with Stubber(ctx.client('mgn')) as stub:
        stub.add_response('describe_jobs', {'items': [
            job('mgnjob-11111111111111111', 'STARTED', [SERVER, OTHER]),
            job('mgnjob-22222222222222222', 'PENDING', [SERVER]),
            job('mgnjob-33333333333333333', 'COMPLETED', [SERVER, OTHER])]}, {})
        assert check('L-FE2EBE17')(ctx)['usage'] == 2
        assert check('L-4FF77426')(ctx)['usage'] == 3
        largest = check('L-F1FD732F')(ctx)
        assert (largest['usage'], largest['resource_id']) == (2, 'mgnjob-11111111111111111')
        per_server = check('L-615F978B')(ctx)
        assert (per_server['usage'], per_server['resource_id']) == (2, SERVER)
        stub.assert_no_pending_responses()


def test_an_unknown_job_status_raises_nodata():
    ctx = context('L-FE2EBE17')
    with Stubber(ctx.client('mgn')) as stub:
        stub.add_response('describe_jobs', {'items': [
            job('mgnjob-11111111111111111', 'PAUSED', [SERVER])]}, {})
        with pytest.raises(NoData, match='unknown status'):
            check('L-FE2EBE17')(ctx)


def test_actions_are_reported_per_server_and_per_template():
    ctx = context('L-0E532B45')
    with Stubber(ctx.client('mgn')) as stub:
        stub.add_response('describe_source_servers',
                          {'items': [server(SERVER), server(OTHER)]}, {})
        stub.add_response('list_source_server_actions', {'items': [
            {'actionID': 'a1'}, {'actionID': 'a2'}]}, {'sourceServerID': SERVER})
        stub.add_response('list_source_server_actions', {'items': [{'actionID': 'a3'}]},
                          {'sourceServerID': OTHER})
        per_server = check('L-0E532B45')(ctx)
        assert (per_server['usage'], per_server['resource_id']) == (2, SERVER)
        stub.add_response('describe_launch_configuration_templates', {'items': [
            {'launchConfigurationTemplateID': TEMPLATE}]}, {})
        stub.add_response('list_template_actions', {'items': [{'actionID': 't1'}]},
                          {'launchConfigurationTemplateID': TEMPLATE})
        per_template = check('L-322CA331')(ctx)
        assert (per_template['usage'], per_template['resource_id']) == (1, TEMPLATE)
        stub.assert_no_pending_responses()
