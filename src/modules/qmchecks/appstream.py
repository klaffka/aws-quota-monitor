"""Amazon AppStream 2.0 resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmchecks.appstream_capacity import CHECKS as CAPACITY_CHECKS


CHECKS = [
    ('L-8A6F32DC', 'Fleets', lambda c: dict(
        usage=len(c.call('appstream', 'describe_fleets', 'Fleets')),
        source='appstream:DescribeFleets', method='ACCOUNT_COUNT')),
    ('L-A8B8B901', 'Stacks', lambda c: dict(
        usage=len(c.call('appstream', 'describe_stacks', 'Stacks')),
        source='appstream:DescribeStacks', method='ACCOUNT_COUNT')),
    ('L-E1182CCA', 'Private images', lambda c: dict(
        usage=len(c.call('appstream', 'describe_images', 'Images',
                         Type='PRIVATE')),
        source='appstream:DescribeImages(Type=PRIVATE)', method='ACCOUNT_COUNT')),
    ('L-3FEADC0C', 'Active fleets', lambda c: dict(
        usage=sum(f.get('State') == 'RUNNING' for f in c.call('appstream', 'describe_fleets', 'Fleets')),
        source='appstream:DescribeFleets(State=RUNNING)', method='ACCOUNT_COUNT')),
    ('L-DE32F884', 'Image builders', lambda c: dict(
        usage=len(c.call('appstream', 'describe_image_builders', 'ImageBuilders')),
        source='appstream:DescribeImageBuilders', method='ACCOUNT_COUNT')),
    ('L-D949908C', 'App block builders', lambda c: dict(
        usage=len(c.call('appstream', 'describe_app_block_builders', 'AppBlockBuilders')),
        source='appstream:DescribeAppBlockBuilders', method='ACCOUNT_COUNT')),
]

ALL_CHECKS = CHECKS + CAPACITY_CHECKS


def get_current_quotastatus_appstream(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'appstream2' for service, _ in context.quotas):
        return []
    checks = CHECKS + [check for check in CAPACITY_CHECKS if ('appstream2', check[0]) in context.quotas]
    return context.run('appstream2', checks, skip)
