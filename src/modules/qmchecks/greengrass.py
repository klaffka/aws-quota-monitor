"""AWS IoT Greengrass V2 components and V1 group scopes.

The component recipe, artifact and deployment document size quotas bound a
single document rather than an inventory.

The group quotas belong to the V1 model, whose group version names each of its
definitions by ARN while the API that reads one takes a definition id and a
version id. The ARN carries both, so it is taken apart under the same rule the
Bedrock batch check follows: the shape is matched whole and anything else
raises NoData, rather than an id being guessed out of a string that does not
look the way it should.
"""
import re

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

GREENGRASS = 'greengrassv2'
GREENGRASS_V1 = 'greengrass'
PRIVATE = 'PRIVATE'
# arn:aws:greengrass:<region>:<account>:/greengrass/definition/<kind>/<id>/versions/<version>
DEFINITION_VERSION = re.compile(
    r'^/greengrass/definition/(?P<kind>devices|functions|resources|subscriptions)'
    r'/(?P<definition>[^/]+)/versions/(?P<version>[^/]+)$')


def definition_ids(arn, kind):
    """Take a definition version ARN apart, or refuse to guess at it."""
    parts = str(arn).split(':', 5)
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != GREENGRASS_V1):
        raise NoData('Greengrass group names a definition version that is not an ARN')
    match = DEFINITION_VERSION.match(parts[5])
    if not match or match.group('kind') != kind:
        raise NoData(f'Greengrass group names no {kind} definition version')
    return match.group('definition'), match.group('version')


def components(ctx):
    """Return the account's own components; AWS-provided ones have their own scope."""
    found = {}
    for component in ctx.call(GREENGRASS, 'list_components', 'components',
                              scope=PRIVATE):
        arn = component.get('arn')
        name = component.get('componentName')
        if not isinstance(arn, str) or not arn:
            raise NoData('Greengrass component is missing its ARN')
        if not isinstance(name, str) or not name:
            raise NoData('Greengrass component is missing its name')
        found[arn] = name
    return found


def versions_per_component(ctx):
    values = []
    for arn, name in components(ctx).items():
        versions = ctx.call(GREENGRASS, 'list_component_versions',
                            'componentVersions', arn=arn)
        for version in versions:
            if not isinstance(version.get('componentVersion'), str):
                raise NoData('Greengrass component version has no version')
        values.append((name, len(versions), None))
    return maximum(values, 'GreengrassComponent',
                   'greengrassv2:ListComponentVersions')


def core_device_name_length(ctx):
    values = []
    for device in ctx.call(GREENGRASS, 'list_core_devices', 'coreDevices'):
        name = device.get('coreDeviceThingName')
        if not isinstance(name, str) or not name:
            raise NoData('Greengrass core device is missing its thing name')
        values.append((name, len(name), None))
    return maximum(values, 'GreengrassCoreDevice', 'greengrassv2:ListCoreDevices')


def _group_definition(ctx, kind, method, key):
    """Yield (group, the definition contents) for every group holding one.

    A group need not hold every kind of definition; one that holds none of this
    kind counts as zero rather than dropping out of the maximum.
    """
    for group in ctx.call(GREENGRASS_V1, 'list_groups', 'Groups'):
        identity = group.get('Id')
        version = group.get('LatestVersion')
        if not identity or not version:
            raise NoData('Greengrass group is missing its id or its latest version')
        definition = ctx.call(GREENGRASS_V1, 'get_group_version', GroupId=identity,
                              GroupVersionId=version).get('Definition') or {}
        arn = definition.get(f'{key}DefinitionVersionArn')
        if not arn:
            yield identity, {}
            continue
        definition_id, version_id = definition_ids(arn, kind)
        detail = ctx.call(GREENGRASS_V1, method,
                          **{f'{key}DefinitionId': definition_id,
                             f'{key}DefinitionVersionId': version_id})
        yield identity, detail.get('Definition') or {}


def per_group(ctx, kind, method, key, member, predicate=None):
    values = []
    for identity, definition in _group_definition(ctx, kind, method, key):
        entries = definition.get(member) or ()
        if predicate:
            entries = [entry for entry in entries if predicate(entry)]
        values.append((identity, len(entries), None))
    return maximum(values, 'GreengrassGroup', f'greengrass:{method}')


def resources_per_function(ctx):
    """The quota bounds one function's resource policies, not the group's."""
    values = []
    for identity, definition in _group_definition(ctx, 'functions',
                                                  'get_function_definition_version',
                                                  'Function'):
        for entry in definition.get('Functions') or ():
            name = entry.get('Id')
            if not name:
                raise NoData('Greengrass function is missing its id')
            environment = (entry.get('FunctionConfiguration') or {}).get('Environment') or {}
            values.append((f'{identity}/{name}',
                           len(environment.get('ResourceAccessPolicies') or ()), None))
    return maximum(values, 'GreengrassFunction', 'greengrass:GetFunctionDefinitionVersion')


CHECKS = [
    ('L-4676BC3D', 'Components',
     lambda ctx: dict(usage=len(components(ctx)),
                      source='greengrassv2:ListComponents', method='ACCOUNT_COUNT')),
    ('L-FC3754BD', 'Versions per component', versions_per_component),
    ('L-AB912DF1', 'Core device thing name length', core_device_name_length),
    ('L-172983AD', 'AWS IoT devices per Greengrass group',
     lambda ctx: per_group(ctx, 'devices', 'get_device_definition_version', 'Device',
                           'Devices')),
    ('L-F7F6CD87', 'Lambda functions per Greengrass group',
     lambda ctx: per_group(ctx, 'functions', 'get_function_definition_version', 'Function',
                           'Functions')),
    ('L-56EE2BF6', 'Resources per Greengrass group',
     lambda ctx: per_group(ctx, 'resources', 'get_resource_definition_version', 'Resource',
                           'Resources')),
    ('L-AC2D5DCC', 'Subscriptions per Greengrass group',
     lambda ctx: per_group(ctx, 'subscriptions', 'get_subscription_definition_version',
                           'Subscription', 'Subscriptions')),
    # AWS names the cloud as the source of a subscription it sends to the group.
    ('L-59276CBA', "Subscriptions with 'cloud' message source per Greengrass group",
     lambda ctx: per_group(ctx, 'subscriptions', 'get_subscription_definition_version',
                           'Subscription', 'Subscriptions',
                           predicate=lambda entry: entry.get('Source') == 'cloud')),
    ('L-966A9851', 'Resources per Lambda function (V1)', resources_per_function),
]


def get_current_quotastatus_greengrass(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'greengrass' for service, _ in context.quotas):
        return []
    return context.run('greengrass', CHECKS, skip)
