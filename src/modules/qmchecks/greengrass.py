"""AWS IoT Greengrass V2 component and core device quotas.

The component recipe, artifact and deployment document size quotas bound a
single document rather than an inventory. The five quotas that count devices,
Lambda functions, resources and subscriptions inside a Greengrass group belong
to the V1 group model, whose definition versions are addressed by ARN while the
API takes a definition id and version id pair; they are left open rather than
measured through ARN parsing.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

GREENGRASS = 'greengrassv2'
PRIVATE = 'PRIVATE'


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


CHECKS = [
    ('L-4676BC3D', 'Components',
     lambda ctx: dict(usage=len(components(ctx)),
                      source='greengrassv2:ListComponents', method='ACCOUNT_COUNT')),
    ('L-FC3754BD', 'Versions per component', versions_per_component),
    ('L-AB912DF1', 'Core device thing name length', core_device_name_length),
]


def get_current_quotastatus_greengrass(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'greengrass' for service, _ in context.quotas):
        return []
    return context.run('greengrass', CHECKS, skip)
