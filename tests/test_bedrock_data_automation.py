from datetime import datetime, UTC
from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import bedrock_data_automation as bda
from modules.qmchecks.bedrock import CHECKS, get_current_quotastatus_bedrock
from modules.qmchecks.ssm import EXTENDED_CHECKS as SSM_CHECKS
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys
from tests.iam_policy import grants

NOW = datetime(2026, 9, 11, tzinfo=UTC)
ARN = 'arn:aws:bedrock:eu-central-1:123456789012:blueprint/abcdefghijkl'
LIB = 'arn:aws:bedrock:eu-central-1:123456789012:data-automation-library/abcdefghijkl'


def context(code='L-D3894D44'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'bedrock', 'QuotaCode': code, 'Value': 100}], account='123456789012')


def blueprint(stage='LIVE', version=None, schema='{}'):
    result = dict(blueprintArn=ARN, blueprintStage=stage, blueprintName='blueprint',
                  creationTime=NOW, lastModifiedTime=NOW, type='DOCUMENT', schema=schema)
    if version is not None:
        result['blueprintVersion'] = version
    return result


def summary(stage='LIVE', version=None):
    return {k: v for k, v in blueprint(stage, version).items() if k not in {'type', 'schema'}}


def test_blueprint_schema_maximum_includes_saved_versions_and_development_stage():
    ctx = context()
    raw = '{ "description": "Grüße PRIVATE_TEXT" }'
    with Stubber(ctx.client(bda.SERVICE)) as stub:
        stub.add_response('list_blueprints', {'blueprints': [summary('LIVE'), summary('DEVELOPMENT')]},
                          {'resourceOwner': 'ACCOUNT', 'blueprintStageFilter': 'ALL'})
        stub.add_response('list_blueprints', {'blueprints': [summary(version='2')], 'nextToken': 'next'},
                          {'blueprintArn': ARN, 'resourceOwner': 'ACCOUNT', 'blueprintStageFilter': 'ALL'})
        stub.add_response('list_blueprints', {'blueprints': [summary(version='2'), summary(version='7')]},
                          {'blueprintArn': ARN, 'resourceOwner': 'ACCOUNT', 'blueprintStageFilter': 'ALL', 'nextToken': 'next'})
        for stage in ['DEVELOPMENT', 'LIVE']:
            stub.add_response('get_blueprint', {'blueprint': blueprint(stage)}, {'blueprintArn': ARN, 'blueprintStage': stage})
        for version, schema in [('2', raw), ('7', '{}')]:
            stub.add_response('get_blueprint', {'blueprint': blueprint(version=version, schema=schema)},
                              {'blueprintArn': ARN, 'blueprintVersion': version})
        result = bda.blueprint_size(ctx)
        assert (result['usage'], result['resource_id']) == (len(raw), ARN+'/blueprintVersion/2')
        assert result['usage'] != len(raw.encode('utf-8'))
        assert 'PRIVATE_TEXT' not in str(result)
        assert bda.blueprint_versions(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('changes', [{'blueprintArn': ARN+'other'}, {'blueprintVersion': '0'},
                                    {'blueprintVersion': 'DRAFT'}, {'blueprintVersion': None}])
def test_unresolved_blueprint_versions_are_not_counted(changes):
    ctx = Mock()
    ctx.call.return_value = [dict(summary(version='1'), **changes)]
    with pytest.raises(NoData):
        bda.versions(ctx, ARN)


@pytest.mark.parametrize('changes', [{'blueprintArn': ARN+'other'}, {'blueprintStage': 'DEVELOPMENT'}, {'schema': None}])
def test_mismatched_blueprint_detail_does_not_emit_usage(changes):
    ctx = Mock()
    ctx.call.side_effect = [[summary()], [], {'blueprint': dict(blueprint(), **changes)}]
    with pytest.raises(NoData):
        bda.blueprint_size(ctx)


def test_failed_saved_blueprint_detail_prevents_partial_collector_sample():
    ctx = context()
    with Stubber(ctx.client(bda.SERVICE)) as stub:
        stub.add_response('list_blueprints', {'blueprints': [summary()]},
                          {'resourceOwner': 'ACCOUNT', 'blueprintStageFilter': 'ALL'})
        stub.add_response('list_blueprints', {'blueprints': [summary(version='1')]},
                          {'blueprintArn': ARN, 'resourceOwner': 'ACCOUNT', 'blueprintStageFilter': 'ALL'})
        stub.add_response('get_blueprint', {'blueprint': blueprint()}, {'blueprintArn': ARN, 'blueprintStage': 'LIVE'})
        stub.add_client_error('get_blueprint', 'AccessDeniedException', expected_params={'blueprintArn': ARN, 'blueprintVersion': '1'})
        row, = get_current_quotastatus_bedrock(ctx=ctx, skip={('bedrock', code) for code, _, _ in CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None


def test_vocabulary_count_sums_all_languages_per_library_and_deduplicates_pages():
    ctx = context('L-EA764586')
    english = {'vocabulary': {'entityId': 'en', 'language': 'EN', 'numOfPhrases': 3, 'lastModifiedTime': NOW}}
    german = {'vocabulary': {'entityId': 'de', 'language': 'DE', 'numOfPhrases': 4, 'lastModifiedTime': NOW}}
    second = LIB[:-1]+'m'
    with Stubber(ctx.client(bda.SERVICE)) as stub:
        stub.add_response('list_data_automation_libraries', {'libraries': [{'libraryArn': LIB, 'creationTime': NOW}], 'nextToken': 'next'}, {})
        stub.add_response('list_data_automation_libraries', {'libraries': [{'libraryArn': LIB, 'creationTime': NOW},
                                                                         {'libraryArn': second, 'creationTime': NOW}]}, {'nextToken': 'next'})
        stub.add_response('list_data_automation_library_entities', {'entities': [english], 'nextToken': 'next'},
                          {'libraryArn': LIB, 'entityType': 'VOCABULARY'})
        stub.add_response('list_data_automation_library_entities', {'entities': [english, german]},
                          {'libraryArn': LIB, 'entityType': 'VOCABULARY', 'nextToken': 'next'})
        stub.add_response('list_data_automation_library_entities', {'entities': []}, {'libraryArn': second, 'entityType': 'VOCABULARY'})
        result = bda.vocabulary_phrases(ctx)
        assert (result['usage'], result['resource_id']) == (7, LIB)
        assert bda.library_count(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('count', [None, True, -1, '3'])
def test_missing_or_invalid_vocabulary_counts_are_not_zero(count):
    ctx = Mock()
    ctx.call.side_effect = [[{'libraryArn': LIB}], [{'vocabulary': {'entityId': 'en', 'numOfPhrases': count}}]]
    with pytest.raises(NoData):
        bda.vocabulary_phrases(ctx)


def test_conflicting_vocabulary_counts_fail_instead_of_using_partial_inventory():
    ctx = Mock()
    ctx.call.side_effect = [[{'libraryArn': LIB}], [{'vocabulary': {'entityId': 'en', 'numOfPhrases': n}} for n in [2, 3]]]
    with pytest.raises(NoData):
        bda.vocabulary_phrases(ctx)


def test_empty_inventories_are_zero_and_new_checks_have_registration_and_permissions():
    ctx = Mock()
    ctx.call.return_value = []
    for _, _, check in bda.CHECKS:
        assert check(ctx)['usage'] == 0
    assert {('bedrock', code) for code, _, _ in bda.CHECKS} <= custom_keys()
    assert {('ssm', code) for code, _, _ in SSM_CHECKS} <= custom_keys()
    for action in ['bedrock:GetBlueprint', 'bedrock:ListDataAutomationLibraries', 'bedrock:ListDataAutomationLibraryEntities',
                   'ssm:ListAssociationVersions', 'ssm:DescribeDocumentPermission']:
        assert grants(f'{action}')
