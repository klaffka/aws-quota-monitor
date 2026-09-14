"""AWS RAM resource-share, association, and permission counts."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def resource_associations(ctx):
    associations = []
    seen = set()
    for item in ctx.call('ram', 'list_resources', 'resources', resourceOwner='SELF'):
        if not isinstance(item, dict):
            raise NoData('RAM resource-association inventory contains an invalid item')
        resource_arn = item.get('arn')
        share_arn = item.get('resourceShareArn')
        if (not isinstance(resource_arn, str) or not resource_arn
                or not isinstance(share_arn, str) or not share_arn):
            raise NoData('RAM resource association is missing an identity')
        identity = (share_arn, resource_arn)
        if identity in seen:
            raise NoData('RAM resource-association inventory contains a duplicate')
        seen.add(identity)
        associations.append(identity)
    return associations


def resource_association_count(ctx):
    return dict(usage=len(resource_associations(ctx)), source='ram:ListResources',
                method='ACCOUNT_COUNT')


def resources_per_share(ctx):
    counts = Counter(share_arn for share_arn, _ in resource_associations(ctx))
    return maximum(((share_arn, count, None) for share_arn, count in counts.items()),
                   'RAMResourceShare', 'ram:ListResources')


def principals_per_share(ctx):
    counts = Counter()
    seen = set()
    for item in ctx.call('ram', 'list_principals', 'principals', resourceOwner='SELF'):
        if not isinstance(item, dict):
            raise NoData('RAM principal-association inventory contains an invalid item')
        principal = item.get('id')
        share_arn = item.get('resourceShareArn')
        if (not isinstance(principal, str) or not principal
                or not isinstance(share_arn, str) or not share_arn):
            raise NoData('RAM principal association is missing an identity')
        identity = (share_arn, principal)
        if identity in seen:
            raise NoData('RAM principal-association inventory contains a duplicate')
        seen.add(identity)
        counts[share_arn] += 1
    return maximum(((share_arn, count, None) for share_arn, count in counts.items()),
                   'RAMResourceShare', 'ram:ListPrincipals')


def customer_permissions(ctx):
    permissions = {}
    for item in ctx.call('ram', 'list_permissions', 'permissions',
                         permissionType='CUSTOMER_MANAGED'):
        if not isinstance(item, dict):
            raise NoData('RAM customer-permission inventory contains an invalid item')
        arn = item.get('arn')
        resource_type = item.get('resourceType')
        if (not isinstance(arn, str) or not arn
                or not isinstance(resource_type, str) or not resource_type
                or item.get('permissionType') != 'CUSTOMER_MANAGED'):
            raise NoData('RAM customer-managed permission is missing required identity data')
        if arn in permissions and permissions[arn] != resource_type:
            raise NoData('RAM customer-managed permission has conflicting resource types')
        permissions[arn] = resource_type
    return permissions


def customer_permission_count(ctx):
    return dict(usage=len(customer_permissions(ctx)), source='ram:ListPermissions',
                method='ACCOUNT_COUNT')


def customer_permissions_per_resource_type(ctx):
    counts = Counter(customer_permissions(ctx).values())
    return maximum(((resource_type, count, None)
                    for resource_type, count in counts.items()),
                   'RAMResourceType', 'ram:ListPermissions')

CHECKS = [
    ('L-595828F9', 'Number of resource shares',
     lambda c: dict(usage=len(c.call('ram', 'get_resource_shares', 'resourceShares', resourceOwner='SELF')),
                    source='ram:GetResourceShares', method='ACCOUNT_COUNT')),
    ('L-8491BF81', 'Number of principal associations',
     lambda c: dict(usage=len(c.call('ram', 'list_principals', 'principals', resourceOwner='SELF')),
                    source='ram:ListPrincipals', method='ACCOUNT_COUNT')),
    ('L-238C96EE', 'Number of pending invitations',
     lambda c: dict(usage=len(c.call('ram', 'get_resource_share_invitations',
                                    'resourceShareInvitations')),
                    source='ram:GetResourceShareInvitations', method='ACCOUNT_COUNT')),
    ('L-1F7F8A25', 'Number of resource associations per resource share',
     resources_per_share),
    ('L-275DAC00', 'Number of principal associations per resource share',
     principals_per_share),
    ('L-2870BE9D', 'Number of custom permissions per resource type',
     customer_permissions_per_resource_type),
    ('L-4A6CEE66', 'Number of resource associations', resource_association_count),
    ('L-9EBA15DD', 'Number of custom permissions', customer_permission_count),
]

def get_current_quotastatus_ram(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ram' for service, _ in context.quotas): return []
    return context.run('ram', CHECKS, skip)
