"""AWS Ground Station regional resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env, maximum


def count(ctx, method, key):
    return dict(usage=len(ctx.call('groundstation', method, key)), source=f'groundstation:{method}', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-5CCF0BC2', 'Config limit', lambda ctx: count(ctx, 'list_configs', 'configList')),
    ('L-5342B9BF', 'Mission profile limit', lambda ctx: count(ctx, 'list_mission_profiles', 'missionProfileList')),
    ('L-98A63A85', 'Dataflow endpoints per group limit',
     lambda ctx: maximum([(g.get('dataflowEndpointGroupId'), len(g.get('endpointsDetails', [])), None)
                          for g in (ctx.call('groundstation', 'list_dataflow_endpoint_groups', 'dataflowEndpointGroupList'))
                          for g in [ctx.call('groundstation', 'get_dataflow_endpoint_group', dataflowEndpointGroupId=g.get('dataflowEndpointGroupId'))]],
                         'DataflowEndpointGroup', 'groundstation:GetDataflowEndpointGroup')),
]


def get_current_quotastatus_groundstation(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'groundstation' for service, _ in context.quotas): return []
    return context.run('groundstation', CHECKS, skip)
