"""Amazon GameLift regional persistent resource inventories."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def fleets(ctx, compute_type=None):
    """Return the fleets, optionally of one compute type.

    ListFleets returns every type behind one identifier list, and the fleet
    quotas count managed EC2 and Anywhere fleets separately.
    """
    attributes = ctx.call('gamelift', 'describe_fleet_attributes', 'FleetAttributes')
    return [fleet for fleet in attributes
            if compute_type is None or fleet.get('ComputeType') == compute_type]


def fleet_count(ctx, compute_type):
    return dict(usage=len(fleets(ctx, compute_type)),
                source=f'gamelift:DescribeFleetAttributes(ComputeType={compute_type})',
                method='ACCOUNT_COUNT')


def compute_per_anywhere_fleet(ctx):
    return maximum([(fleet['FleetId'],
                     len(ctx.call('gamelift', 'list_compute', 'ComputeList',
                                  FleetId=fleet['FleetId'])), None)
                    for fleet in fleets(ctx, 'ANYWHERE')],
                   'GameLiftFleet', 'gamelift:ListCompute')


def locations_per_fleet(ctx):
    return maximum([(fleet['FleetId'],
                     len(ctx.call('gamelift', 'describe_fleet_location_attributes',
                                  'LocationAttributes', FleetId=fleet['FleetId'])), None)
                    for fleet in fleets(ctx)],
                   'GameLiftFleet', 'gamelift:DescribeFleetLocationAttributes')


def game_servers_per_group(ctx):
    return maximum([(group['GameServerGroupName'],
                     len(ctx.call('gamelift', 'list_game_servers', 'GameServers',
                                  GameServerGroupName=group['GameServerGroupName'])), None)
                    for group in ctx.call('gamelift', 'list_game_server_groups',
                                          'GameServerGroups')],
                   'GameLiftGameServerGroup', 'gamelift:ListGameServers')


def destinations_per_queue(ctx):
    return maximum([(queue['Name'], len(queue.get('Destinations') or ()), None)
                    for queue in ctx.call('gamelift', 'describe_game_session_queues',
                                          'GameSessionQueues')],
                   'GameLiftGameSessionQueue', 'gamelift:DescribeGameSessionQueues')


CHECKS = [
    ('L-FDDD1260', 'Managed EC2 fleets per region', lambda c: fleet_count(c, 'EC2')),
    ('L-593688D9', 'Anywhere fleets per region', lambda c: fleet_count(c, 'ANYWHERE')),
    ('L-0536A98D', 'Compute per Anywhere fleet', compute_per_anywhere_fleet),
    ('L-55650DB7', 'Locations in a fleet per region', locations_per_fleet),
    ('L-51AF299A', 'Game servers per game server group', game_servers_per_group),
    ('L-BB62CF1D', 'Queue destinations per game session queue', destinations_per_queue),
    ('L-8D885299', 'Game server groups',
     lambda c: dict(usage=len(c.call('gamelift', 'list_game_server_groups', 'GameServerGroups')),
                    source='gamelift:ListGameServerGroups', method='ACCOUNT_COUNT')),
    ('L-90D24F1B', 'Builds',
     lambda c: dict(usage=len(c.call('gamelift', 'list_builds', 'Builds')),
                    source='gamelift:ListBuilds', method='ACCOUNT_COUNT')),
    ('L-22451070', 'Game session queues',
     lambda c: dict(usage=len(c.call('gamelift', 'describe_game_session_queues', 'GameSessionQueues')),
                    source='gamelift:DescribeGameSessionQueues', method='ACCOUNT_COUNT')),
    ('L-AED4A06A', 'Aliases',
     lambda c: dict(usage=len(c.call('gamelift', 'list_aliases', 'Aliases')),
                    source='gamelift:ListAliases', method='ACCOUNT_COUNT')),
    ('L-293B0017', 'Scripts',
     lambda c: dict(usage=len(c.call('gamelift', 'list_scripts', 'Scripts')),
                    source='gamelift:ListScripts', method='ACCOUNT_COUNT')),
    ('L-C6F4238C', 'Custom locations',
     lambda c: dict(usage=len(c.call('gamelift', 'list_locations', 'Locations')),
                    source='gamelift:ListLocations', method='ACCOUNT_COUNT')),
    ('L-73F6E300', 'Matchmaking configurations',
     lambda c: dict(usage=len(c.call('gamelift', 'describe_matchmaking_configurations', 'Configurations')),
                    source='gamelift:DescribeMatchmakingConfigurations', method='ACCOUNT_COUNT')),
    ('L-8AE49BBD', 'Matchmaking rule sets',
     lambda c: dict(usage=len(c.call('gamelift', 'describe_matchmaking_rule_sets', 'RuleSets')),
                    source='gamelift:DescribeMatchmakingRuleSets', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_gamelift(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'gamelift' for service, _ in context.quotas):
        return []
    return context.run('gamelift', CHECKS, skip)
