"""AWS RoboMaker regional application inventories.

botocore no longer ships a `robomaker` client; the calls are still attempted so
the checks recover by themselves if the SDK restores the service.
"""
from modules.qmcore.aws import CheckContext, sdk_call, session_from_env

ROBOMAKER = 'robomaker'


def count(ctx, method, key):
    return dict(usage=len(sdk_call(ctx, ROBOMAKER, method, key)),
                source=f'robomaker:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-D6554FB1', 'Simulation applications',
     lambda ctx: count(ctx, 'list_simulation_applications',
                       'simulationApplicationSummaries')),
    ('L-E5D0EA7D', 'Robot applications',
     lambda ctx: count(ctx, 'list_robot_applications', 'robotApplicationSummaries')),
]


def get_current_quotastatus_robomaker(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == ROBOMAKER for service, _ in context.quotas):
        return []
    return context.run(ROBOMAKER, CHECKS, skip)
