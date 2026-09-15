"""Every check below once called its API with parameters botocore rejects.

``ctx.run`` turns the resulting ParamValidationError into an ERROR measurement,
so the check failed on every collector run without ever failing a test. The
stubs here match the request body, so a wrong parameter set cannot pass.
"""
from datetime import datetime, timezone

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import (amplifyuibuilder, datazone, elasticbeanstalk, fms,
                              forecast, securityhub, transfer)
from modules.qmchecks.ec2 import ec2
from modules.qmcore.aws import CheckContext

MOMENT = datetime(2026, 9, 15, tzinfo=timezone.utc)


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def test_launch_templates_are_listed_without_an_owner_filter():
    """DescribeLaunchTemplates takes no OwnerId; it already returns own templates."""
    ctx = context('ec2', 'L-FB451C26')
    with Stubber(ctx.client('ec2')) as stub:
        stub.add_response('describe_launch_templates',
                          {'LaunchTemplates': [{'LaunchTemplateId': 'lt-1'}]}, {})
        assert ec2.launch_template_count(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_security_hub_members_are_listed_not_fetched_by_account_id():
    """GetMembers requires the very account IDs the check is trying to discover."""
    ctx = context('securityhub', 'L-6E4302A5')
    with Stubber(ctx.client('securityhub')) as stub:
        stub.add_response('list_members', {'Members': [{'AccountId': '111111111111'}]}, {})
        assert check(securityhub, 'L-6E4302A5')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('code, method, key, item', [
    ('L-0E131699', 'list_apps_lists', 'AppsLists', {'ListId': 'l' * 36}),
    ('L-C6CF2DBB', 'list_protocols_lists', 'ProtocolsLists', {'ListId': 'l' * 36}),
])
def test_firewall_manager_lists_pass_the_required_page_size(code, method, key, item):
    ctx = context('fms', code)
    with Stubber(ctx.client('fms')) as stub:
        stub.add_response(method, {key: [item]},
                          {'DefaultLists': False, 'MaxResults': fms.PAGE_SIZE})
        assert check(fms, code)(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


ASSET = {'assetItem': {'domainId': 'dzd-1', 'identifier': 'a', 'name': 'asset',
                       'typeIdentifier': 't', 'typeRevision': '1', 'owningProjectId': 'p'}}
GLOSSARY = {'glossaryItem': {'domainId': 'dzd-1', 'id': 'g', 'name': 'glossary',
                             'owningProjectId': 'p', 'status': 'ENABLED'}}
ASSET_TYPE = {'assetTypeItem': {'domainId': 'dzd-1', 'name': 'type', 'revision': '1',
                                'formsOutput': {}, 'owningProjectId': 'p'}}


@pytest.mark.parametrize('code, operation, params, item', [
    ('L-06335BC6', 'search', {'domainIdentifier': 'dzd-1', 'searchScope': 'ASSET'}, ASSET),
    ('L-2C2845D2', 'search', {'domainIdentifier': 'dzd-1', 'searchScope': 'GLOSSARY'}, GLOSSARY),
    ('L-9EF33583', 'search_types',
     {'domainIdentifier': 'dzd-1', 'managed': True, 'searchScope': 'ASSET_TYPE'}, ASSET_TYPE),
])
def test_datazone_inventories_use_the_search_operations(code, operation, params, item):
    """DataZone ships no list_assets/list_glossaries/list_asset_types at all."""
    ctx = context('datazone', code)
    with Stubber(ctx.client('datazone')) as stub:
        stub.add_response('list_domains',
                          {'items': [{'id': 'dzd-1', 'arn': 'arn:domain', 'name': 'domain',
                                      'managedAccountId': '123456789012',
                                      'status': 'AVAILABLE', 'createdAt': MOMENT}]}, {})
        stub.add_response(operation, {'items': [item, item]}, params)
        result = check(datazone, code)(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'dzd-1')
        stub.assert_no_pending_responses()


def test_forecast_backtest_exports_use_the_job_listing():
    """The operation is ListPredictorBacktestExportJobs, not ...Exports."""
    ctx = context('forecast', 'L-E1AC300F')
    with Stubber(ctx.client('forecast')) as stub:
        stub.add_response('list_predictor_backtest_export_jobs',
                          {'PredictorBacktestExportJobs': [{'PredictorBacktestExportJobArn': 'arn:a'}]}, {})
        assert check(forecast, 'L-E1AC300F')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_amplify_ui_builder_counts_per_app_and_backend_environment():
    """ListThemes requires environmentName; the check only ever sent appId."""
    ctx = context('amplifyuibuilder', 'L-429DD3BA')
    with Stubber(ctx.client('amplify')) as amplify, \
            Stubber(ctx.client('amplifyuibuilder')) as builder:
        amplify.add_response('list_apps', {'apps': [APP]}, {})
        amplify.add_response('list_backend_environments',
                             {'backendEnvironments': [BACKEND]}, {'appId': 'app-1'})
        theme = {'appId': 'app-1', 'environmentName': 'staging', 'id': 't', 'name': 'theme'}
        builder.add_response('list_themes', {'entities': [theme, dict(theme, id='u')]},
                             {'appId': 'app-1', 'environmentName': 'staging'})
        result = check(amplifyuibuilder, 'L-429DD3BA')(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'app-1/staging')
        amplify.assert_no_pending_responses()
        builder.assert_no_pending_responses()


APP = {'appId': 'app-1', 'appArn': 'arn:app', 'name': 'app', 'description': '',
       'repository': '', 'platform': 'WEB', 'createTime': MOMENT, 'updateTime': MOMENT,
       'environmentVariables': {}, 'defaultDomain': 'example.com',
       'enableBranchAutoBuild': False, 'enableBasicAuth': False}
BACKEND = {'backendEnvironmentArn': 'arn:env', 'environmentName': 'staging',
           'createTime': MOMENT, 'updateTime': MOMENT}


def test_transfer_agreements_are_counted_per_server():
    """ListAgreements requires a ServerId, so the account total sums the servers."""
    ctx = context('transfer', 'L-C08739CA')
    with Stubber(ctx.client('transfer')) as stub:
        stub.add_response('list_servers',
                          {'Servers': [{'ServerId': 's-' + '1' * 17, 'Arn': 'arn:aws:transfer:eu-central-1:1'},
                                       {'ServerId': 's-' + '2' * 17, 'Arn': 'arn:aws:transfer:eu-central-1:2'}]}, {})
        stub.add_response('list_agreements', {'Agreements': [{'AgreementId': 'a-' + '1' * 17}]},
                          {'ServerId': 's-' + '1' * 17})
        stub.add_response('list_agreements', {'Agreements': [{'AgreementId': 'a-' + '2' * 17},
                                                             {'AgreementId': 'a-' + '3' * 17}]},
                          {'ServerId': 's-' + '2' * 17})
        assert check(transfer, 'L-C08739CA')(ctx)['usage'] == 3
        stub.assert_no_pending_responses()


def test_custom_platform_versions_filter_on_the_platform_status_type():
    """PlatformFilter names the attribute Type; Name is not one of its members."""
    ctx = context('elasticbeanstalk', 'L-E593A077')
    with Stubber(ctx.client('elasticbeanstalk')) as stub:
        stub.add_response('list_platform_versions',
                          {'PlatformSummaryList': [{'PlatformArn': 'arn:platform'}]},
                          {'Filters': [{'Type': 'PlatformStatus', 'Operator': '=',
                                        'Values': ['Ready']}]})
        assert check(elasticbeanstalk, 'L-E593A077')(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_datazone_environments_are_listed_per_project():
    """ListEnvironments requires a projectIdentifier alongside the domain."""
    ctx = context('datazone', 'L-EDF6298B')
    with Stubber(ctx.client('datazone')) as stub:
        stub.add_response('list_domains',
                          {'items': [{'id': 'dzd-1', 'arn': 'arn:domain', 'name': 'domain',
                                      'managedAccountId': '123456789012',
                                      'status': 'AVAILABLE', 'createdAt': MOMENT}]}, {})
        stub.add_response('list_projects', {'items': [{'id': 'prj-1', 'domainId': 'dzd-1',
                                                       'name': 'project', 'createdBy': 'me'}]},
                          {'domainIdentifier': 'dzd-1'})
        stub.add_response('list_environments', {'items': [{'id': 'env-1', 'name': 'env',
                                                           'createdBy': 'me', 'provider': 'aws',
                                                           'projectId': 'prj-1',
                                                           'domainId': 'dzd-1'}]},
                          {'domainIdentifier': 'dzd-1', 'projectIdentifier': 'prj-1'})
        result = check(datazone, 'L-EDF6298B')(ctx)
        assert (result['usage'], result['resource_id']) == (1, 'dzd-1')
        stub.assert_no_pending_responses()
