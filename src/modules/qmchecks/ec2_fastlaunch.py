"""EC2 fast launch parallel instance launch quota."""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

EC2 = 'ec2'


def parallel_launches(ctx):
    """Report the largest parallel launch count configured on a fast launch image."""
    values = []
    for image in ctx.call(EC2, 'describe_fast_launch_images', 'FastLaunchImages'):
        identity = image.get('ImageId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Fast launch image is missing its identity')
        configured = image.get('MaxParallelLaunches')
        if not isinstance(configured, int) or isinstance(configured, bool):
            raise NoData('Fast launch image has no parallel launch count')
        values.append((identity, configured, None))
    return maximum(values, 'EC2Image', 'ec2:DescribeFastLaunchImages')


CHECKS = [('L-DC79B53E', 'Parallel instance launches', parallel_launches)]


def get_current_quotastatus_ec2fastlaunch(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ec2fastlaunch' for service, _ in context.quotas):
        return []
    return context.run('ec2fastlaunch', CHECKS, skip)
