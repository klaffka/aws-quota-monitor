"""AWS Deadline Cloud regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def farms(ctx):
    return ctx.call('deadline', 'list_farms', 'farms')


def account_count(ctx, method, key):
    return dict(usage=len(ctx.call('deadline', method, key)), source=f'deadline:{method}', method='ACCOUNT_COUNT')


def per_farm(ctx, method, key):
    values = []
    for farm in farms(ctx):
        farm_id = farm.get('farmId') or farm.get('id')
        resources = ctx.call('deadline', method, key, farmId=farm_id)
        values.append((farm_id, len(resources), None))
    return maximum(values, 'DeadlineFarm', f'deadline:{method}')


CHECKS = [
    ('L-2DEF7E07', 'Farms per region', lambda ctx: account_count(ctx, 'list_farms', 'farms')),
    ('L-F4ED6ADC', 'Monitors per region', lambda ctx: account_count(ctx, 'list_monitors', 'monitors')),
    ('L-F0DF6BC2', 'License endpoints per region', lambda ctx: account_count(ctx, 'list_license_endpoints', 'licenseEndpoints')),
    ('L-55A8E463', 'Fleets per farm', lambda ctx: per_farm(ctx, 'list_fleets', 'fleets')),
    ('L-5E4FD3A4', 'Queues per farm', lambda ctx: per_farm(ctx, 'list_queues', 'queues')),
    ('L-48CC9B8E', 'Workers per farm', lambda ctx: per_farm(ctx, 'list_workers', 'workers')),
    ('L-5369B22C', 'Jobs per farm', lambda ctx: per_farm(ctx, 'list_jobs', 'jobs')),
    ('L-86C1F13E', 'Budgets per farm', lambda ctx: per_farm(ctx, 'list_budgets', 'budgets')),
    ('L-8148A0DC', 'Storage profiles per farm', lambda ctx: per_farm(ctx, 'list_storage_profiles', 'storageProfiles')),
]


def get_current_quotastatus_deadline(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'deadline' for service, _ in context.quotas):
        return []
    return context.run('deadline', CHECKS, skip)
