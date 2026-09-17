"""AWS IoT FleetWise regional account resources and per-parent scopes.

`Number of state templates for each vehicle` stays in the audit: the templates
are attached per vehicle, and a fleet holds as many vehicles as it likes.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


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


def _named(ctx, method, key, subject):
    for entry in ctx.call('iotfleetwise', method, key):
        name = entry.get('name')
        if not isinstance(name, str) or not name:
            raise NoData(f'IoT FleetWise {subject} is missing its name')
        yield name


def nodes_per_signal_catalog(ctx):
    """GetSignalCatalog reports the totals, so the nodes are never listed."""
    values = []
    for name in _named(ctx, 'list_signal_catalogs', 'summaries', 'signal catalog'):
        counts = ctx.call('iotfleetwise', 'get_signal_catalog', name=name).get('nodeCounts') or {}
        total = counts.get('totalNodes')
        if not isinstance(total, int):
            raise NoData('IoT FleetWise signal catalog reports no node count')
        values.append((name, total, None))
    return maximum(values, 'IoTFleetWiseSignalCatalog', 'iotfleetwise:GetSignalCatalog')


def per_campaign(ctx, member):
    values = []
    for name in _named(ctx, 'list_campaigns', 'campaignSummaries', 'campaign'):
        detail = ctx.call('iotfleetwise', 'get_campaign', name=name)
        if detail.get('name') != name:
            raise NoData('IoT FleetWise campaign detail has a different identity')
        values.append((name, len(detail.get(member) or ()), None))
    return maximum(values, 'IoTFleetWiseCampaign', 'iotfleetwise:GetCampaign')


def per_state_template(ctx, member):
    """All three state template quotas are answered by the same detail call."""
    values = []
    for name in _named(ctx, 'list_state_templates', 'summaries', 'state template'):
        detail = ctx.call('iotfleetwise', 'get_state_template', identifier=name)
        if detail.get('name') != name:
            raise NoData('IoT FleetWise state template detail has a different identity')
        values.append((name, len(detail.get(member) or ()), None))
    return maximum(values, 'IoTFleetWiseStateTemplate', 'iotfleetwise:GetStateTemplate')


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
    ('L-FE285ED4', 'Number of nodes in a signal catalog for each account in an AWS Region',
     nodes_per_signal_catalog),
    ('L-86E70888', 'Number of signals in a campaign for each account in an AWS Region.',
     lambda ctx: per_campaign(ctx, 'signalsToCollect')),
    ('L-A0A396E0', 'Number of partitions in a campaign configured to store and forward.',
     lambda ctx: per_campaign(ctx, 'dataPartitions')),
    ('L-300E5FB4', 'Number of signals for a state template in an AWS Region.',
     lambda ctx: per_state_template(ctx, 'stateTemplateProperties')),
    ('L-6BE0F5F7', 'Number of data dimensions for a state template in an AWS Region.',
     lambda ctx: per_state_template(ctx, 'dataExtraDimensions')),
    ('L-0FDD56E9', 'Number of metadata dimensions for a state template in an AWS Region.',
     lambda ctx: per_state_template(ctx, 'metadataExtraDimensions')),
]


def get_current_quotastatus_iotfleetwise(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotfleetwise' for service, _ in context.quotas):
        return []
    return context.run('iotfleetwise', CHECKS, skip)
