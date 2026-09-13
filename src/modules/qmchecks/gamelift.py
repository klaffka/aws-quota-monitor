"""Amazon GameLift regional persistent resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-FDDD1260', 'Managed EC2 fleets',
     lambda c: dict(usage=len(c.call('gamelift', 'list_fleets', 'FleetIds')),
                    source='gamelift:ListFleets', method='ACCOUNT_COUNT')),
    ('L-8D885299', 'Game server groups',
     lambda c: dict(usage=len(c.call('gamelift', 'list_game_server_groups', 'GameServerGroups')),
                    source='gamelift:ListGameServerGroups', method='ACCOUNT_COUNT')),
    ('L-90D24F1B', 'Builds',
     lambda c: dict(usage=len(c.call('gamelift', 'list_builds', 'Builds')),
                    source='gamelift:ListBuilds', method='ACCOUNT_COUNT')),
    ('L-22451070', 'Game session queues',
     lambda c: dict(usage=len(c.call('gamelift', 'describe_game_session_queues', 'GameSessionQueues')),
                    source='gamelift:DescribeGameSessionQueues', method='ACCOUNT_COUNT')),
    ('L-AED4A06', 'Aliases',
     lambda c: dict(usage=len(c.call('gamelift', 'list_aliases', 'Aliases')),
                    source='gamelift:ListAliases', method='ACCOUNT_COUNT')),
    ('L-293B0017', 'Scripts',
     lambda c: dict(usage=len(c.call('gamelift', 'list_scripts', 'Scripts')),
                    source='gamelift:ListScripts', method='ACCOUNT_COUNT')),
    ('L-C6F4238C', 'Custom locations',
     lambda c: dict(usage=len(c.call('gamelift', 'list_locations', 'Locations')),
                    source='gamelift:ListLocations', method='ACCOUNT_COUNT')),
    ('L-73F6E300', 'Matchmaking configurations',
     lambda c: dict(usage=len(c.call('gamelift', 'describe_matchmaking_configurations', 'MatchmakingConfigurations')),
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
