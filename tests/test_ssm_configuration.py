from unittest.mock import Mock

import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import ssm
from modules.qmcore.aws import CheckContext, NoData


def context(code='L-F5EE067E'):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': 'ssm', 'QuotaCode': code, 'Value': 1000}], account='123456789012')


def test_shares_merge_both_response_lists_paginate_and_use_distinct_quota_scopes():
    ctx = context()
    with Stubber(ctx.client('ssm')) as stub:
        stub.add_response('list_documents', {'DocumentIdentifiers': [{'Name': 'one'}, {'Name': 'two'}, {'Name': 'one'}]},
                          {'Filters': [{'Key': 'Owner', 'Values': ['Self']}]})
        stub.add_response('describe_document_permission',
                          {'AccountIds': ['111111111111', 'all'], 'AccountSharingInfoList': [
                              {'AccountId': '111111111111', 'SharedDocumentVersion': '1'},
                              {'AccountId': '222222222222', 'SharedDocumentVersion': '2'}], 'NextToken': 'next'},
                          {'Name': 'one', 'PermissionType': 'Share'})
        stub.add_response('describe_document_permission',
                          {'AccountSharingInfoList': [{'AccountId': '333333333333', 'SharedDocumentVersion': '1'}]},
                          {'Name': 'one', 'PermissionType': 'Share', 'NextToken': 'next'})
        stub.add_response('describe_document_permission', {'AccountIds': ['All', '444444444444']},
                          {'Name': 'two', 'PermissionType': 'Share'})
        result = ssm.document_shares(ctx)
        assert (result['usage'], result['resource_id']) == (3, 'one')
        assert ssm.document_shares(ctx, public=True)['usage'] == 2
        assert '111111111111' not in str(result)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('page', [{}, {'AccountIds': None}, {'AccountIds': ['unknown']}, {'AccountSharingInfoList': [{}]}])
def test_missing_or_invalid_permissions_are_not_zero(page):
    ctx = Mock()
    ctx.call.return_value = page
    with pytest.raises(NoData):
        ssm.document_permissions(ctx, 'document')


def test_repeated_permission_token_is_rejected():
    ctx = Mock()
    ctx.call.return_value = {'AccountIds': [], 'NextToken': 'same'}
    with pytest.raises(NoData, match='pagination'):
        ssm.document_permissions(ctx, 'document')
    assert ctx.call.call_count == 2


def test_failed_later_permission_page_does_not_emit_partial_count():
    ctx = context()
    with Stubber(ctx.client('ssm')) as stub:
        stub.add_response('list_documents', {'DocumentIdentifiers': [{'Name': 'one'}]},
                          {'Filters': [{'Key': 'Owner', 'Values': ['Self']}]})
        stub.add_response('describe_document_permission', {'AccountIds': ['111111111111'], 'NextToken': 'next'},
                          {'Name': 'one', 'PermissionType': 'Share'})
        stub.add_client_error('describe_document_permission', 'AccessDeniedException', expected_params={
            'Name': 'one', 'PermissionType': 'Share', 'NextToken': 'next'})
        row, = ssm.get_current_quotastatus_ssm(ctx=ctx, skip={('ssm', code) for code, _, _ in ssm.CHECKS})
        assert row['qualityStatus'] == 'ERROR'
        assert row['usageValue'] is None
        stub.assert_no_pending_responses()


def test_package_versions_filter_document_type_deduplicate_and_do_not_use_largest_version_number():
    ctx = context('L-2D5C8B1F')
    with Stubber(ctx.client('ssm')) as stub:
        stub.add_response('list_documents', {'DocumentIdentifiers': [{'Name': 'package', 'DocumentType': 'Package'},
                                                                    {'Name': 'command', 'DocumentType': 'Command'}]},
                          {'Filters': [{'Key': 'Owner', 'Values': ['Self']}]})
        stub.add_response('list_document_versions', {'DocumentVersions': [{'Name': 'package', 'DocumentVersion': '7'}], 'NextToken': 'next'},
                          {'Name': 'package'})
        stub.add_response('list_document_versions', {'DocumentVersions': [{'Name': 'package', 'DocumentVersion': '7'},
                                                                         {'Name': 'package', 'DocumentVersion': '12'}]},
                          {'Name': 'package', 'NextToken': 'next'})
        assert ssm.document_versions(ctx, packages_only=True)['usage'] == 2
        stub.assert_no_pending_responses()


def test_association_versions_count_retained_versions_per_association():
    ctx = context('L-FB5A4449')
    identity = '12345678-1234-1234-1234-123456789012'
    with Stubber(ctx.client('ssm')) as stub:
        stub.add_response('list_associations', {'Associations': [{'AssociationId': identity}]}, {})
        stub.add_response('list_association_versions', {'AssociationVersions': [
            {'AssociationId': identity, 'AssociationVersion': '1'},
            {'AssociationId': identity, 'AssociationVersion': '9'}]}, {'AssociationId': identity})
        result = ssm.association_versions(ctx)
        assert (result['usage'], result['resource_id']) == (2, identity)
        stub.assert_no_pending_responses()


@pytest.mark.parametrize('versions', [[], [{}], [{'Name': 'other', 'DocumentVersion': '1'}], [{'DocumentVersion': '$LATEST'}]])
def test_incomplete_ssm_version_inventories_are_unknown(versions):
    with pytest.raises(NoData):
        ssm.version_total(versions, 'document', 'Name', 'DocumentVersion')


def test_parameter_policy_count_includes_finished_policies_without_reading_values():
    ctx = context('L-C84673D4')
    with Stubber(ctx.client('ssm')) as stub:
        stub.add_response('describe_parameters', {'Parameters': [
            {'Name': '/legacy'}, {'Name': '/empty', 'Tier': 'Advanced'},
            {'Name': '/configured', 'Tier': 'Advanced', 'Policies': [
                {'PolicyType': 'Expiration', 'PolicyStatus': 'Finished', 'PolicyText': 'PRIVATE_TEXT'},
                {'PolicyType': 'NoChangeNotification', 'PolicyStatus': 'Pending'}]}]}, {})
        result = ssm.parameter_policies(ctx)
        assert (result['usage'], result['resource_id']) == (2, '/configured')
        assert 'PRIVATE_TEXT' not in str(result)
        stub.assert_no_pending_responses()


def test_unknown_parameter_tier_and_missing_package_type_do_not_hide_resources():
    ctx = Mock()
    ctx.call.return_value = [{'Name': 'unknown', 'Tier': 'Intelligent-Tiering'}]
    with pytest.raises(NoData):
        ssm.parameter_policies(ctx)
    with pytest.raises(NoData):
        ssm.document_versions(ctx, packages_only=True)
