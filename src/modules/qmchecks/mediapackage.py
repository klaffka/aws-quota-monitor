"""AWS Elemental MediaPackage packaging group scopes and harvest jobs.

The VOD packaging resources live behind the `mediapackage-vod` client while the
harvest jobs live behind `mediapackage`; the quotas are all filed under the one
`mediapackage` service code.

The ingest stream and track quotas stay in the audit: they bound what a running
channel receives, which no inventory reports after the fact.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

VOD = 'mediapackage-vod'
LIVE = 'mediapackage'


def packaging_groups(ctx):
    return dict(usage=len(ctx.call(VOD, 'list_packaging_groups', 'PackagingGroups')),
                source='mediapackage-vod:ListPackagingGroups', method='ACCOUNT_COUNT')


def per_packaging_group(ctx, method, key):
    """Both listings answer for the account and name their packaging group."""
    counts = {}
    for entry in ctx.call(VOD, method, key):
        group = entry.get('PackagingGroupId')
        if not isinstance(group, str) or not group:
            raise NoData(f'MediaPackage {key} entry names no packaging group')
        counts[group] = counts.get(group, 0) + 1
    return maximum([(group, count, None) for group, count in sorted(counts.items())],
                   'MediaPackagePackagingGroup', f'mediapackage-vod:{method}')


def running_harvest_jobs(ctx):
    """MediaPackage filters by status server side, so only the running ones."""
    jobs = ctx.call(LIVE, 'list_harvest_jobs', 'HarvestJobs', IncludeStatus='IN_PROGRESS')
    return dict(usage=len(jobs), source='mediapackage:ListHarvestJobs',
                method='ACCOUNT_COUNT')


CHECKS = [
    ('L-66FFDBE4', 'Packaging groups', packaging_groups),
    ('L-1E1258F1', 'Packaging configurations per packaging group',
     lambda ctx: per_packaging_group(ctx, 'list_packaging_configurations',
                                     'PackagingConfigurations')),
    ('L-563EE697', 'Assets per packaging group',
     lambda ctx: per_packaging_group(ctx, 'list_assets', 'Assets')),
    ('L-B1B90B42', 'Concurrent harvest jobs', running_harvest_jobs),
]


def get_current_quotastatus_mediapackage(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediapackage' for service, _ in context.quotas):
        return []
    return context.run('mediapackage', CHECKS, skip)
