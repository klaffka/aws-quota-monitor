
import pytest

from modules.qmchecks.ram import (
    customer_permission_count,
    customer_permissions_per_resource_type,
    principals_per_share,
    resource_association_count,
    resources_per_share,
)
from modules.qmcore.aws import NoData
from tests.iam_policy import grants


class RAMContext:
    resources = [
        {'arn': 'arn:resource:one', 'resourceShareArn': 'arn:share:a'},
        {'arn': 'arn:resource:two', 'resourceShareArn': 'arn:share:a'},
        {'arn': 'arn:resource:one', 'resourceShareArn': 'arn:share:b'},
    ]
    principals = [
        {'id': '111111111111', 'resourceShareArn': 'arn:share:a'},
        {'id': '222222222222', 'resourceShareArn': 'arn:share:a'},
        {'id': '111111111111', 'resourceShareArn': 'arn:share:b'},
    ]
    permissions = [
        {'arn': 'arn:permission:one', 'resourceType': 'ec2:Subnet',
         'permissionType': 'CUSTOMER_MANAGED', 'version': '2'},
        {'arn': 'arn:permission:two', 'resourceType': 'ec2:Subnet',
         'permissionType': 'CUSTOMER_MANAGED', 'version': '1'},
        {'arn': 'arn:permission:three', 'resourceType': 'imagebuilder:Component',
         'permissionType': 'CUSTOMER_MANAGED', 'version': '1'},
    ]

    def call(self, service, method, key=None, **kwargs):
        assert service == 'ram'
        if method == 'list_resources':
            assert key == 'resources' and kwargs == {'resourceOwner': 'SELF'}
            return self.resources
        if method == 'list_principals':
            assert key == 'principals' and kwargs == {'resourceOwner': 'SELF'}
            return self.principals
        if method == 'list_permissions':
            assert key == 'permissions'
            assert kwargs == {'permissionType': 'CUSTOMER_MANAGED'}
            return self.permissions
        raise AssertionError(method)


def test_ram_associations_count_each_share_membership():
    ctx = RAMContext()
    assert resource_association_count(ctx)['usage'] == 3
    assert (resources_per_share(ctx)['usage'],
            resources_per_share(ctx)['resource_id']) == (2, 'arn:share:a')
    assert (principals_per_share(ctx)['usage'],
            principals_per_share(ctx)['resource_id']) == (2, 'arn:share:a')


def test_ram_customer_permissions_are_unique_and_grouped_by_resource_type():
    ctx = RAMContext()
    assert customer_permission_count(ctx)['usage'] == 3
    result = customer_permissions_per_resource_type(ctx)
    assert (result['usage'], result['resource_id']) == (2, 'ec2:Subnet')
    assert result['meta'] is None


def test_ram_configuration_rejects_incomplete_or_conflicting_inventories():
    ctx = RAMContext()
    ctx.resources = [*ctx.resources, dict(ctx.resources[0])]
    with pytest.raises(NoData, match='contains a duplicate'):
        resources_per_share(ctx)

    ctx = RAMContext()
    ctx.permissions = [*ctx.permissions, {
        'arn': 'arn:permission:one', 'resourceType': 'ec2:SecurityGroup',
        'permissionType': 'CUSTOMER_MANAGED', 'version': '1',
    }]
    with pytest.raises(NoData, match='conflicting resource types'):
        customer_permission_count(ctx)


def test_ram_configuration_check_has_read_permission():
    assert grants('ram:ListPermissions')
