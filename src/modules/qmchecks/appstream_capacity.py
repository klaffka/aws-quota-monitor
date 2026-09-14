"""AppStream instance, platform and image quotas with explicit scope matching."""
from functools import partial

from modules.qmchecks.appstream_quotas import INSTANCE_QUOTAS, PLATFORM_QUOTAS
from modules.qmcore.aws import NoData, maximum


def required(item, key):
    value = item.get(key)
    if value is None or value == '':
        raise NoData(f'AppStream inventory is missing {key}')
    return value


def count_value(item, key):
    value = required(item, key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise NoData(f'AppStream inventory has invalid {key}')
    return value


def image_type(ctx, resource):
    """ImageType distinguishes NATIVE and BYOL using the same stream.* type."""
    if resource.get('ImageArn'):
        selector = {'Arns': [resource['ImageArn']]}
    elif resource.get('ImageName'):
        selector = {'Names': [resource['ImageName']]}
    else:
        raise NoData('AppStream resource has no image identity for quota scope')
    images = ctx.call('appstream', 'describe_images', 'Images', **selector)
    if len(images) != 1:
        raise NoData('AppStream image identity could not be resolved uniquely')
    value = required(images[0], 'ImageType')
    if value not in {'NATIVE', 'CUSTOM', 'BYOL'}:
        raise NoData(f'Unknown AppStream image type: {value}')
    return value


def fleet_instances(fleet):
    """Use actual provisioned instances, including idle On-Demand capacity.

    During provisioning or draining, desired and actual counts can differ and
    neither alone proves quota reservation usage. Keep that uncertainty visible.
    Session slots are never substituted for instance counts on multi-session fleets.
    """
    if required(fleet, 'State') == 'STOPPED':
        return 0
    if fleet['State'] != 'RUNNING':
        raise NoData('AppStream fleet is starting or stopping')
    capacity = required(fleet, 'ComputeCapacityStatus')
    if capacity.get('Draining', 0):
        raise NoData('AppStream fleet has draining instances')
    if fleet.get('MaxSessionsPerInstance', 1) > 1:
        actual = count_value(capacity, 'Running')
    else:
        actual = count_value(capacity, 'Available') + count_value(capacity, 'InUse')
    if actual != count_value(capacity, 'Desired'):
        raise NoData('AppStream fleet actual and desired instance capacity differ')
    return actual


def instance_usage(ctx, instance_type, quota_image_type, inventory):
    method, key = ('describe_fleets', 'Fleets') if inventory == 'fleet' else (
        'describe_image_builders', 'ImageBuilders')
    usage = 0
    for resource in ctx.call('appstream', method, key):
        if inventory == 'fleet':
            if required(resource, 'FleetType') == 'ELASTIC':
                continue
            if resource['FleetType'] not in {'ALWAYS_ON', 'ON_DEMAND'}:
                raise NoData('Unknown AppStream fleet type')
            if required(resource, 'State') == 'STOPPED':
                continue
        if required(resource, 'InstanceType') != instance_type:
            continue
        # Imported instance types can only use CUSTOM images. stream.* types
        # require image metadata because native and BYOL quotas are separate.
        actual_image_type = image_type(ctx, resource) if instance_type.startswith('stream.') else 'CUSTOM'
        if actual_image_type != quota_image_type:
            continue
        if inventory == 'fleet':
            usage += fleet_instances(resource)
        else:
            # A running builder is unambiguously consuming an instance. The
            # public API does not expose a quota reservation flag for stopped,
            # failed or transitional builders; never invent their contribution.
            if required(resource, 'State') != 'RUNNING':
                raise NoData('AppStream image-builder instance accounting is unresolved outside RUNNING state')
            usage += 1
    return dict(usage=usage, source=f'appstream:{method}+ImageType', method='ACCOUNT_COUNT',
                meta={'instanceType': instance_type, 'imageType': quota_image_type,
                      'inventory': inventory})


def platform_usage(ctx, instance_type, platform, inventory):
    method, key = ('describe_fleets', 'Fleets') if inventory == 'elastic_session' else (
        'describe_app_block_builders', 'AppBlockBuilders')
    usage = 0
    for resource in ctx.call('appstream', method, key):
        if inventory == 'elastic_session' and required(resource, 'FleetType') != 'ELASTIC':
            continue
        if required(resource, 'InstanceType') != instance_type:
            continue
        if required(resource, 'Platform') != platform:
            continue
        if inventory == 'app_block_builder':
            # This quota is the number of builder resources, not running VMs.
            usage += 1
            continue
        fleet_name = required(resource, 'Name')
        if required(resource, 'State') == 'STOPPED':
            continue
        sessions = set()
        for stack in ctx.call('appstream', 'list_associated_stacks', 'Names', FleetName=fleet_name):
            # Omitting AuthenticationType lists API-authenticated sessions only.
            for auth in ('API', 'SAML', 'USERPOOL', 'AWS_AD'):
                for session in ctx.call('appstream', 'describe_sessions', 'Sessions',
                                        FleetName=fleet_name, StackName=stack, AuthenticationType=auth):
                    state = required(session, 'State')
                    if state == 'EXPIRED':
                        continue
                    if state not in {'ACTIVE', 'PENDING'}:
                        raise NoData(f'Unknown AppStream session state: {state}')
                    # Disconnected sessions still occupy their session slot.
                    sessions.add(required(session, 'Id'))
        usage += len(sessions)
    source = 'appstream:DescribeFleets+ListAssociatedStacks+DescribeSessions' if inventory == 'elastic_session' else 'appstream:DescribeAppBlockBuilders'
    return dict(usage=usage, source=source, method='ACCOUNT_COUNT',
                meta={'instanceType': instance_type, 'platform': platform, 'inventory': inventory})


def image_copies(ctx):
    images = ctx.call('appstream', 'describe_images', 'Images', Type='PRIVATE')
    return dict(usage=sum(required(image, 'State') == 'COPYING' for image in images),
                source='appstream:DescribeImages', method='ACCOUNT_COUNT')


def image_sharing(ctx):
    values = []
    for image in ctx.call('appstream', 'describe_images', 'Images', Type='PRIVATE'):
        accounts = set()
        for permission in ctx.call('appstream', 'describe_image_permissions', 'SharedImagePermissionsList',
                                   Name=required(image, 'Name')):
            flags = required(permission, 'imagePermissions')
            if flags.get('allowFleet') or flags.get('allowImageBuilder'):
                accounts.add(required(permission, 'sharedAccountId'))
        values.append((image['Name'], len(accounts), None))
    return maximum(values, 'AppStreamImage', 'appstream:DescribeImagePermissions')


CHECKS = [(code, f'{instance_type} {image_type} {inventory} instances',
           partial(instance_usage, instance_type=instance_type, quota_image_type=image_type, inventory=inventory))
          for code, instance_type, image_type, inventory in INSTANCE_QUOTAS]
CHECKS += [(code, f'{instance_type} {platform} {inventory}',
            partial(platform_usage, instance_type=instance_type, platform=platform, inventory=inventory))
           for code, instance_type, platform, inventory in PLATFORM_QUOTAS]
CHECKS += [
    ('L-60244546', 'Concurrent image copies per destination Region', image_copies),
    ('L-99A44980', 'Image sharing limit', image_sharing),
    ('L-6A8C9986', 'Users in the user pool', lambda c: dict(
        usage=len(c.call('appstream', 'describe_users', 'Users', AuthenticationType='USERPOOL')),
        source='appstream:DescribeUsers', method='ACCOUNT_COUNT')),
]
