"""AWS IoT FleetWise regional account resource quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def resource_count(ctx, method, key):
    return dict(usage=len(ctx.call('iotfleetwise', method, key)),
                source=f'iotfleetwise:{method}', method='ACCOUNT_COUNT')


def vehicles_per_fleet(ctx):
    values = []
    fleets = ctx.call('iotfleetwise', 'list_fleets', 'fleetSummaries')
    for fleet in fleets:
        fleet_id = fleet.get('id') or fleet.get('fleetId')
        vehicles = ctx.call('iotfleetwise', 'list_vehicles_in_fleet', 'vehicles', fleetId=fleet_id)
        values.append((fleet_id, len(vehicles), None))
    return maximum(values, 'IoTFleetWiseFleet', 'iotfleetwise:ListVehiclesInFleet')


CHECKS = [
    ('L-85AC6579', 'Number of vehicles in a fleet for each account', vehicles_per_fleet),
    ('L-17D821A8', 'Number of campaigns for each account',
     lambda ctx: resource_count(ctx, 'list_campaigns', 'campaignSummaries')),
    ('L-8AFF6AA2', 'Number of signal catalogs for each account',
     lambda ctx: resource_count(ctx, 'list_signal_catalogs', 'summaries')),
    ('L-72103FA9', 'Number of model manifests for each account',
     lambda ctx: resource_count(ctx, 'list_model_manifests', 'summaries')),
    ('L-9EE083E6', 'Number of decoder manifests for each account',
     lambda ctx: resource_count(ctx, 'list_decoder_manifests', 'summaries')),
    ('L-9EDEDFF3', 'Number of state templates for each account',
     lambda ctx: resource_count(ctx, 'list_state_templates', 'summaries')),
]


def get_current_quotastatus_iotfleetwise(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotfleetwise' for service, _ in context.quotas):
        return []
    return context.run('iotfleetwise', CHECKS, skip)
