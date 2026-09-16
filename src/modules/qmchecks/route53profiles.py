"""Route 53 Profiles regional resource and association quotas."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


PROFILE_SHARE_STATUSES = {'NOT_SHARED', 'SHARED_BY_ME', 'SHARED_WITH_ME'}
ASSOCIATION_STATUSES = {'COMPLETE', 'CREATING', 'UPDATING', 'DELETING', 'DELETED'}
RESOURCE_TYPES = {
    'FIREWALL_RULE_GROUP', 'HOSTED_ZONE', 'RESOLVER_QUERY_LOG_CONFIG',
    'RESOLVER_RULE', 'VPC_ENDPOINT',
}


def profiles(ctx, *, owned_only=False):
    result = {}
    for item in ctx.call('route53profiles', 'list_profiles', 'ProfileSummaries'):
        if not isinstance(item, dict):
            raise NoData('Route 53 Profiles inventory contains an invalid item')
        profile_id = item.get('Id')
        arn = item.get('Arn')
        share_status = item.get('ShareStatus')
        if (not isinstance(profile_id, str) or not profile_id
                or not isinstance(arn, str) or not arn
                or share_status not in PROFILE_SHARE_STATUSES):
            raise NoData('Route 53 Profile is missing required identity data')
        if profile_id in result:
            raise NoData('Route 53 Profiles inventory contains a duplicate')
        result[profile_id] = item
    if owned_only:
        return {profile_id: item for profile_id, item in result.items()
                if item['ShareStatus'] != 'SHARED_WITH_ME'}
    return result


def profile_count(ctx):
    return dict(usage=len(profiles(ctx, owned_only=True)),
                source='route53profiles:ListProfiles', method='ACCOUNT_COUNT')


def _active(status, subject):
    if status == 'FAILED' or status not in ASSOCIATION_STATUSES:
        raise NoData(f'Route 53 Profiles {subject} has an unresolved status')
    return status != 'DELETED'


def vpcs_per_profile(ctx):
    known_profiles = profiles(ctx)
    counts = Counter()
    identities = set()
    for item in ctx.call('route53profiles', 'list_profile_associations',
                         'ProfileAssociations'):
        if not isinstance(item, dict):
            raise NoData('Route 53 Profiles VPC-association inventory has an invalid item')
        identity = item.get('Id')
        profile_id = item.get('ProfileId')
        resource_id = item.get('ResourceId')
        if (not isinstance(identity, str) or not identity
                or profile_id not in known_profiles
                or not isinstance(resource_id, str) or not resource_id):
            raise NoData('Route 53 Profiles VPC association is missing its parent identity')
        if identity in identities:
            raise NoData('Route 53 Profiles VPC-association inventory contains a duplicate')
        identities.add(identity)
        if _active(item.get('Status'), 'VPC association'):
            counts[profile_id] += 1
    return maximum(((profile_id, counts[profile_id], None)
                    for profile_id in known_profiles),
                   'Route53Profile', 'route53profiles:ListProfileAssociations')


def _resource_counts(ctx, resource_type):
    owned_profiles = profiles(ctx, owned_only=True)
    counts = Counter()
    identities = set()
    for profile_id in owned_profiles:
        items = ctx.call('route53profiles', 'list_profile_resource_associations',
                         'ProfileResourceAssociations', ProfileId=profile_id)
        for item in items:
            if not isinstance(item, dict):
                raise NoData('Route 53 Profiles resource inventory has an invalid item')
            identity = item.get('Id')
            item_type = item.get('ResourceType')
            resource_arn = item.get('ResourceArn')
            if (not isinstance(identity, str) or not identity
                    or item.get('ProfileId') != profile_id
                    or not isinstance(resource_arn, str) or not resource_arn
                    or item_type not in RESOURCE_TYPES):
                raise NoData('Route 53 Profiles resource association is inconsistent')
            if identity in identities:
                raise NoData('Route 53 Profiles resource inventory contains a duplicate')
            identities.add(identity)
            if item_type == resource_type and _active(
                    item.get('Status'), 'resource association'):
                counts[profile_id] += 1
    return owned_profiles, counts


def resources_per_profile(ctx, resource_type):
    owned_profiles, counts = _resource_counts(ctx, resource_type)
    return maximum(((profile_id, counts[profile_id], None)
                    for profile_id in owned_profiles),
                   'Route53Profile',
                   'route53profiles:ListProfileResourceAssociations')


CHECKS = [
    ('L-D9B2356C', 'Route 53 Profiles per account per Region', profile_count),
    ('L-9BABD1D7', 'VPC to Route 53 Profile associations per Region',
     vpcs_per_profile),
    ('L-BA3424AB', 'Private hosted zone associations to a Route 53 Profile',
     lambda ctx: resources_per_profile(ctx, 'HOSTED_ZONE')),
    ('L-0B404E57', 'VPC Endpoint associations to a Route 53 Profile',
     lambda ctx: resources_per_profile(ctx, 'VPC_ENDPOINT')),
]


def get_current_quotastatus_route53profiles(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'route53profiles' for service, _ in context.quotas):
        return []
    return context.run('route53profiles', CHECKS, skip)
