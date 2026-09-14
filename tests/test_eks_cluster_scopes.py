import boto3
import pytest
from botocore.stub import Stubber

from modules.qmchecks.eks import CHECKS, registered_clusters
from modules.qmcore.aws import CheckContext


def test_native_and_connected_clusters_use_distinct_inventory_scopes():
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), account='123456789012')
    with Stubber(ctx.client('eks')) as stub:
        stub.add_response('list_clusters', {'clusters': ['native']}, {})
        stub.add_response('list_clusters', {'clusters': ['native'], 'nextToken': 'next'},
                          {'include': ['all']})
        stub.add_response('list_clusters', {'clusters': ['external']},
                          {'include': ['all'], 'nextToken': 'next'})
        stub.add_response('describe_cluster', {'cluster': {'name': 'native'}}, {'name': 'native'})
        stub.add_response('describe_cluster', {'cluster': {'name': 'external',
                          'connectorConfig': {'provider': 'OTHER'}}}, {'name': 'external'})
        native = next(fn for code, _, fn in CHECKS if code == 'L-1194D53C')
        assert native(ctx)['usage'] == 1
        assert registered_clusters(ctx)['usage'] == 1
        stub.assert_no_pending_responses()


def test_registered_cluster_description_failure_is_not_counted_as_native():
    ctx = CheckContext(boto3.Session(region_name='eu-central-1'), account='123456789012')
    with Stubber(ctx.client('eks')) as stub:
        stub.add_response('list_clusters', {'clusters': ['external']}, {'include': ['all']})
        stub.add_client_error('describe_cluster', service_error_code='AccessDeniedException',
                              expected_params={'name': 'external'})
        with pytest.raises(Exception, match='AccessDeniedException'):
            registered_clusters(ctx)
