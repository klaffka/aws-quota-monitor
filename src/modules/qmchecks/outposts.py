"""AWS Outposts regional site and per-site resource quotas."""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env


def _validate_arn(arn, ctx, resource_type, resource_id, subject):
    if arn is None:
        return
    parts = arn.split(':', 5) if isinstance(arn, str) else []
    if (len(parts) != 6 or parts[0] != 'arn' or parts[2] != 'outposts'
            or parts[3] != ctx.region or parts[4] != ctx.account
            or parts[5] != f'{resource_type}/{resource_id}'):
        raise NoData(f'AWS Outposts {subject} has an inconsistent ARN')


def sites(ctx):
    result = {}
    arns = set()
    for item in ctx.call('outposts', 'list_sites', 'Sites'):
        if not isinstance(item, dict):
            raise NoData('AWS Outposts site inventory contains an invalid item')
        site_id = item.get('SiteId')
        if (not isinstance(site_id, str) or not site_id
                or item.get('AccountId') != ctx.account):
            raise NoData('AWS Outposts site is missing required account identity data')
        _validate_arn(item.get('SiteArn'), ctx, 'site', site_id, 'site')
        if site_id in result:
            if result[site_id] != item:
                raise NoData('AWS Outposts site changed during pagination')
            continue
        arn = item.get('SiteArn')
        if arn is not None and arn in arns:
            raise NoData('AWS Outposts site inventory contains a duplicate ARN')
        result[site_id] = item
        if arn is not None:
            arns.add(arn)
    return result


def site_count(ctx):
    return dict(usage=len(sites(ctx)), source='outposts:ListSites',
                method='ACCOUNT_COUNT')


def outposts_per_site(ctx):
    known_sites = sites(ctx)
    counts = Counter()
    outposts = {}
    arns = set()
    for item in ctx.call('outposts', 'list_outposts', 'Outposts'):
        if not isinstance(item, dict):
            raise NoData('AWS Outposts Outpost inventory contains an invalid item')
        outpost_id = item.get('OutpostId')
        site_id = item.get('SiteId')
        status = item.get('LifeCycleStatus')
        if (not isinstance(outpost_id, str) or not outpost_id
                or item.get('OwnerId') != ctx.account
                or site_id not in known_sites
                or not isinstance(status, str) or not status):
            raise NoData('AWS Outposts Outpost is missing required owner or parent data')
        _validate_arn(item.get('OutpostArn'), ctx, 'outpost', outpost_id, 'Outpost')
        _validate_arn(item.get('SiteArn'), ctx, 'site', site_id, 'Outpost parent')
        known_site_arn = known_sites[site_id].get('SiteArn')
        if (known_site_arn is not None and item.get('SiteArn') not in {None, known_site_arn}):
            raise NoData('AWS Outposts Outpost has an inconsistent site parent')
        if outpost_id in outposts:
            if outposts[outpost_id] != item:
                raise NoData('AWS Outposts Outpost changed during pagination')
            continue
        arn = item.get('OutpostArn')
        if arn is not None and arn in arns:
            raise NoData('AWS Outposts Outpost inventory contains a duplicate ARN')
        outposts[outpost_id] = item
        if arn is not None:
            arns.add(arn)
        counts[site_id] += 1
    return maximum(((site_id, counts[site_id], None) for site_id in known_sites),
                   'OutpostSite', 'outposts:ListSites+ListOutposts')


CHECKS = [
    ('L-3D389D34', 'Outpost sites', site_count),
    ('L-0B277C74', 'Outposts per site', outposts_per_site),
]


def get_current_quotastatus_outposts(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'outposts' for service, _ in context.quotas):
        return []
    return context.run('outposts', CHECKS, skip)
