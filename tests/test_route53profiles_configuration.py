from pathlib import Path

import pytest

from modules.qmchecks.route53profiles import (
    profile_count,
    resources_per_profile,
    vpcs_per_profile,
)
from modules.qmcore.aws import NoData


class ProfilesContext:
    def __init__(self):
        self.profile_items = [
            {'Id': 'profile-a', 'Arn': 'arn:profile:a', 'ShareStatus': 'NOT_SHARED'},
            {'Id': 'profile-b', 'Arn': 'arn:profile:b', 'ShareStatus': 'SHARED_BY_ME'},
            {'Id': 'profile-c', 'Arn': 'arn:profile:c', 'ShareStatus': 'SHARED_WITH_ME'},
        ]
        self.vpcs = [
            self.association('vpc-a', 'profile-a', 'vpc-1'),
            self.association('vpc-b', 'profile-a', 'vpc-2', 'DELETING'),
            self.association('vpc-c', 'profile-b', 'vpc-3'),
            self.association('vpc-d', 'profile-b', 'vpc-4', 'DELETED'),
        ]
        self.resources = {
            'profile-a': [
                self.resource('resource-a', 'profile-a', 'HOSTED_ZONE'),
                self.resource('resource-b', 'profile-a', 'HOSTED_ZONE', 'UPDATING'),
                self.resource('resource-c', 'profile-a', 'VPC_ENDPOINT'),
                self.resource('resource-d', 'profile-a', 'RESOLVER_RULE'),
            ],
            'profile-b': [
                self.resource('resource-e', 'profile-b', 'HOSTED_ZONE'),
                self.resource('resource-f', 'profile-b', 'VPC_ENDPOINT'),
                self.resource('resource-g', 'profile-b', 'VPC_ENDPOINT', 'CREATING'),
                self.resource('resource-h', 'profile-b', 'VPC_ENDPOINT', 'DELETED'),
            ],
        }

    @staticmethod
    def association(identity, profile, resource, status='COMPLETE'):
        return {'Id': identity, 'ProfileId': profile, 'ResourceId': resource,
                'Status': status}

    @staticmethod
    def resource(identity, profile, resource_type, status='COMPLETE'):
        return {'Id': identity, 'ProfileId': profile,
                'ResourceArn': f'arn:resource:{identity}',
                'ResourceType': resource_type, 'Status': status}

    def call(self, service, method, key=None, **kwargs):
        assert service == 'route53profiles'
        if method == 'list_profiles':
            assert key == 'ProfileSummaries' and not kwargs
            return self.profile_items
        if method == 'list_profile_associations':
            assert key == 'ProfileAssociations' and not kwargs
            return self.vpcs
        if method == 'list_profile_resource_associations':
            assert key == 'ProfileResourceAssociations'
            return self.resources[kwargs['ProfileId']]
        raise AssertionError(method)


def test_route53_profile_count_excludes_profiles_shared_with_this_account():
    assert profile_count(ProfilesContext())['usage'] == 2


def test_route53_vpc_associations_use_active_maximum_per_profile():
    result = vpcs_per_profile(ProfilesContext())
    assert (result['usage'], result['resource_id']) == (2, 'profile-a')
    assert result['meta'] is None


def test_route53_resources_are_typed_and_maximized_per_owned_profile():
    ctx = ProfilesContext()
    hosted_zones = resources_per_profile(ctx, 'HOSTED_ZONE')
    endpoints = resources_per_profile(ctx, 'VPC_ENDPOINT')
    assert (hosted_zones['usage'], hosted_zones['resource_id']) == (2, 'profile-a')
    assert (endpoints['usage'], endpoints['resource_id']) == (2, 'profile-b')
    assert hosted_zones['meta'] is endpoints['meta'] is None


def test_route53_profiles_reject_duplicate_and_inconsistent_associations():
    ctx = ProfilesContext()
    ctx.vpcs.append(dict(ctx.vpcs[0]))
    with pytest.raises(NoData, match='contains a duplicate'):
        vpcs_per_profile(ctx)

    ctx = ProfilesContext()
    ctx.resources['profile-a'][0]['ProfileId'] = 'profile-b'
    with pytest.raises(NoData, match='is inconsistent'):
        resources_per_profile(ctx, 'HOSTED_ZONE')


def test_route53_profiles_reject_unresolved_association_states():
    ctx = ProfilesContext()
    ctx.vpcs[0]['Status'] = 'FAILED'
    with pytest.raises(NoData, match='unresolved status'):
        vpcs_per_profile(ctx)

    ctx = ProfilesContext()
    ctx.resources['profile-a'][0]['Status'] = 'FUTURE_STATE'
    with pytest.raises(NoData, match='unresolved status'):
        resources_per_profile(ctx, 'HOSTED_ZONE')


def test_route53_profiles_configuration_has_read_permissions():
    policy = (Path(__file__).parents[1] / 'deployment/main.tf').read_text(encoding='utf-8')
    assert '"route53profiles:ListProfileAssociations"' in policy
    assert '"route53profiles:ListProfileResourceAssociations"' in policy
