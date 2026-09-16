import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks import dax, textract
from modules.qmchecks import license_manager_user_subscriptions as lmus
from modules.qmcore.aws import CheckContext, NoData
from modules.qmcore.registry import custom_keys

PROVIDER = {'ActiveDirectoryIdentityProvider': {'DirectoryId': 'd-1234567890'}}
INSTANCE = 'i-00000000000000001'


def context(service, code):
    return CheckContext(boto3.Session(region_name='eu-central-1'),
                        [{'ServiceCode': service, 'QuotaCode': code, 'Value': 100}],
                        account='123456789012')


def check(module, code):
    return next(fn for quota, _, fn in module.CHECKS if quota == code)


def cluster(name, nodes):
    return {'ClusterName': name, 'TotalNodes': nodes, 'ActiveNodes': nodes,
            'Status': 'available'}


def test_dax_nodes_are_reported_per_cluster_and_in_total():
    for code, expected_usage, expected_id in (('L-87AEEBB5', 5, 'big'),
                                              ('L-AB139030', 8, None)):
        ctx = context('dax', code)
        with Stubber(ctx.client('dax')) as stub:
            stub.add_response('describe_clusters', {'Clusters': [
                cluster('small', 3), cluster('big', 5)]}, {})
            result = check(dax, code)(ctx)
            assert result['usage'] == expected_usage, code
            assert result.get('resource_id') == expected_id, code
            stub.assert_no_pending_responses()


def test_a_dax_cluster_without_a_node_count_raises_nodata():
    ctx = context('dax', 'L-87AEEBB5')
    with Stubber(ctx.client('dax')) as stub:
        stub.add_response('describe_clusters', {'Clusters': [
            {'ClusterName': 'broken', 'Status': 'available'}]}, {})
        with pytest.raises(NoData, match='no node count'):
            check(dax, 'L-87AEEBB5')(ctx)


def test_dax_subnets_are_counted_per_subnet_group():
    ctx = context('dax', 'L-E34C284B')
    with Stubber(ctx.client('dax')) as stub:
        stub.add_response('describe_subnet_groups', {'SubnetGroups': [
            {'SubnetGroupName': 'one', 'Subnets': [{'SubnetIdentifier': 'subnet-1'}]},
            {'SubnetGroupName': 'two', 'Subnets': [
                {'SubnetIdentifier': 'subnet-2'}, {'SubnetIdentifier': 'subnet-3'}]}]}, {})
        result = dax.subnets_per_subnet_group(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'two')
        stub.assert_no_pending_responses()


def product_user(username, product):
    return {'Username': username, 'Product': product, 'IdentityProvider': PROVIDER,
            'Status': 'ACTIVE'}


def test_product_subscriptions_are_matched_regardless_of_spelling():
    ctx = context('license-manager-user-subscriptions', 'L-79A245D6')
    with Stubber(ctx.client('license-manager-user-subscriptions')) as stub:
        stub.add_response('list_identity_providers', {'IdentityProviderSummaries': [
            {'IdentityProvider': PROVIDER, 'Settings': {
                'Subnets': ['subnet-1'], 'SecurityGroupId': 'sg-0123456789abcdef0'},
             'Product': 'VISUAL_STUDIO_ENTERPRISE', 'Status': 'ACTIVE'}]}, {})
        stub.add_response('list_product_subscriptions', {'ProductUserSummaries': [
            product_user('alice', 'VISUAL_STUDIO_ENTERPRISE'),
            product_user('bob', 'Visual Studio Enterprise'),
            product_user('carol', 'OFFICE_PROFESSIONAL_PLUS')]},
            {'IdentityProvider': PROVIDER})
        # Both spellings of the same product count towards its quota.
        assert check(lmus, 'L-79A245D6')(ctx)['usage'] == 2
        stub.assert_no_pending_responses()


def test_instance_associations_are_counted_per_user():
    ctx = context('license-manager-user-subscriptions', 'L-8BE7CFDB')
    with Stubber(ctx.client('license-manager-user-subscriptions')) as stub:
        stub.add_response('list_identity_providers', {'IdentityProviderSummaries': [
            {'IdentityProvider': PROVIDER, 'Settings': {
                'Subnets': ['subnet-1'], 'SecurityGroupId': 'sg-0123456789abcdef0'},
             'Product': 'VISUAL_STUDIO_ENTERPRISE', 'Status': 'ACTIVE'}]}, {})
        stub.add_response('list_instances', {'InstanceSummaries': [
            {'InstanceId': INSTANCE, 'Status': 'ACTIVE', 'Products': ['VS']},
            {'InstanceId': 'i-00000000000000002', 'Status': 'ACTIVE',
             'Products': ['VS']}]}, {})
        for instance in (INSTANCE, 'i-00000000000000002'):
            stub.add_response('list_user_associations', {'InstanceUserSummaries': [
                {'Username': 'alice', 'InstanceId': instance,
                 'IdentityProvider': PROVIDER, 'Status': 'ASSOCIATED'}]},
                {'InstanceId': instance, 'IdentityProvider': PROVIDER})
        result = lmus.instance_associations_per_user(ctx)
        assert (result['usage'], result['resource_id']) == (2, 'alice')
        stub.assert_no_pending_responses()


def test_textract_counts_only_adapter_versions_still_being_created():
    ctx = context('textract', 'L-E6985921')
    with Stubber(ctx.client('textract')) as stub:
        stub.add_response('list_adapter_versions', {'AdapterVersions': [
            {'AdapterId': 'adapter-00001', 'AdapterVersion': '1', 'Status': 'CREATION_IN_PROGRESS'},
            {'AdapterId': 'adapter-00001', 'AdapterVersion': '2', 'Status': 'ACTIVE'},
            {'AdapterId': 'adapter-00002', 'AdapterVersion': '1', 'Status': 'CREATION_ERROR'}]}, {})
        assert textract.in_progress_adapter_versions(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_an_unknown_adapter_version_status_raises_nodata():
    ctx = context('textract', 'L-E6985921')
    with Stubber(ctx.client('textract')) as stub:
        stub.add_response('list_adapter_versions', {'AdapterVersions': [
            {'AdapterId': 'adapter-00001', 'AdapterVersion': '1', 'Status': 'MARINATING'}]}, {})
        with pytest.raises(NoData, match='unknown status'):
            textract.in_progress_adapter_versions(ctx)


def test_every_new_check_is_registered_for_reporting():
    for module, service in ((dax, 'dax'), (textract, 'textract'),
                            (lmus, 'license-manager-user-subscriptions')):
        registered = {code for name, code in custom_keys() if name == service}
        assert {code for code, _, _ in module.CHECKS} <= registered, service
