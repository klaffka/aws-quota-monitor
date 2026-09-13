"""AWS RoboMaker regional application inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


def count(ctx, method, key):
    return dict(usage=len(ctx.call('robomaker', method, key)), source=f'robomaker:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-D6554FB1', 'Simulation applications', lambda ctx: count(ctx, 'list_simulation_applications', 'simulationApplicationSummaries')),
    ('L-E5D0EA7D', 'Robot applications', lambda ctx: count(ctx, 'list_robot_applications', 'robotApplicationSummaries')),
]


def get_current_quotastatus_robomaker(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'robomaker' for service, _ in context.quotas): return []
    return context.run('robomaker', CHECKS, skip)
