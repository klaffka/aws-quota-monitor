"""Amazon Connect outbound campaign quotas, counted per Connect instance."""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CAMPAIGNS = 'connectcampaignsv2'
CAMPAIGN_STATES = {'Initialized', 'Running', 'Paused', 'Stopped', 'Failed', 'Completed'}
# A stopped, failed or completed campaign no longer runs against the instance.
ACTIVE_STATES = {'Initialized', 'Running', 'Paused'}
BATCH = 25


def campaigns(ctx):
    found = {}
    for campaign in ctx.call(CAMPAIGNS, 'list_campaigns', 'campaignSummaryList'):
        identity = campaign.get('id')
        instance = campaign.get('connectInstanceId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Connect campaign is missing its identity')
        if not isinstance(instance, str) or not instance:
            raise NoData('Connect campaign names no instance')
        found[identity] = instance
    return found


def _per_instance(counts):
    return maximum(((instance, count, None) for instance, count in counts.items()),
                   'ConnectInstance', 'connectcampaignsv2:ListCampaigns')


def total_campaigns_per_instance(ctx):
    return _per_instance(Counter(campaigns(ctx).values()))


def active_campaigns_per_instance(ctx):
    """Ask for the state of every campaign, which the summaries omit."""
    inventory = campaigns(ctx)
    identities = sorted(inventory)
    counts = Counter()
    for offset in range(0, len(identities), BATCH):
        batch = identities[offset:offset + BATCH]
        response = ctx.call(CAMPAIGNS, 'get_campaign_state_batch', campaignIds=batch)
        for item in response.get('successfulRequests') or []:
            identity, state = item.get('campaignId'), item.get('state')
            if identity not in inventory:
                raise NoData('Connect campaign state names an unknown campaign')
            if state not in CAMPAIGN_STATES:
                raise NoData('Connect campaign has an unknown state')
            if state in ACTIVE_STATES:
                counts[inventory[identity]] += 1
        if response.get('failedRequests'):
            raise NoData('Connect campaign state could not be read')
    return _per_instance(counts)


CHECKS = [
    ('L-31C1321D', 'Total campaigns per instance', total_campaigns_per_instance),
    ('L-7F7B4C39', 'Active campaigns per instance', active_campaigns_per_instance),
]


def get_current_quotastatus_connect_campaigns(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'connect-campaigns' for service, _ in context.quotas):
        return []
    return context.run('connect-campaigns', CHECKS, skip)
