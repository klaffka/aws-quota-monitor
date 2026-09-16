"""MediaConvert regional resource inventories and queue occupancy.

ListQueues reports each queue's progressing and submitted job counts, so the
concurrency quotas are answered without walking the job history.
"""
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

SERVICE = 'mediaconvert'
SOURCE_QUEUES = 'mediaconvert:ListQueues'


def _queues(ctx):
    for entry in ctx.call(SERVICE, 'list_queues', 'Queues'):
        name = entry.get('Name')
        if not isinstance(name, str) or not name:
            raise NoData('MediaConvert queue is missing its name')
        running = entry.get('ProgressingJobsCount')
        if not isinstance(running, int):
            raise NoData('MediaConvert queue has no progressing job count')
        yield name, entry, running


def progressing_jobs(ctx):
    return dict(usage=sum(running for _name, _entry, running in _queues(ctx)),
                source=SOURCE_QUEUES, method='ACCOUNT_SUM')


def progressing_jobs_per_queue(ctx, plan):
    return maximum([(name, running, None) for name, entry, running in _queues(ctx)
                    if entry.get('PricingPlan') == plan],
                   'MediaConvertQueue', SOURCE_QUEUES)


def default_queue_jobs(ctx):
    """AWS marks the one queue it creates as SYSTEM; the rest are CUSTOM."""
    return maximum([(name, running, None) for name, entry, running in _queues(ctx)
                    if entry.get('Type') == 'SYSTEM'],
                   'MediaConvertQueue', SOURCE_QUEUES)


def reserved_slots(ctx):
    values = []
    for name, entry, _running in _queues(ctx):
        if entry.get('PricingPlan') != 'RESERVED':
            continue
        plan = entry.get('ReservationPlan') or {}
        slots = plan.get('ReservedSlots')
        if not isinstance(slots, int):
            raise NoData('MediaConvert reserved queue has no reserved slot count')
        values.append((name, slots, None))
    return maximum(values, 'MediaConvertQueue', SOURCE_QUEUES)


def custom_presets(ctx):
    presets = ctx.call(SERVICE, 'list_presets', 'Presets')
    return dict(usage=sum(preset.get('Type') == 'CUSTOM' for preset in presets),
                source='mediaconvert:ListPresets', method='ACCOUNT_COUNT')


CHECKS = [
    ('L-44E8E4BC', 'Queues per AWS Region',
     lambda c: dict(usage=len(c.call(SERVICE, 'list_queues', 'Queues')),
                    source=SOURCE_QUEUES, method='ACCOUNT_COUNT')),
    ('L-FFA964F8', 'Custom job templates',
     lambda c: dict(usage=len(c.call(SERVICE, 'list_job_templates', 'JobTemplates')),
                    source='mediaconvert:ListJobTemplates', method='ACCOUNT_COUNT')),
    ('L-89D4C825', 'Concurrent jobs per account', progressing_jobs),
    ('L-1D14865F', 'Concurrent jobs per on-demand queue',
     lambda ctx: progressing_jobs_per_queue(ctx, 'ON_DEMAND')),
    ('L-032C4FB4', 'Concurrent jobs per on-demand queue, default', default_queue_jobs),
    ('L-1AE7DAF9', 'Reserved transcode slots (RTS) per AWS Region, per queue',
     reserved_slots),
    ('L-8CFEB230', 'Custom output presets', custom_presets),
]


def get_current_quotastatus_mediaconvert(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mediaconvert' for service, _ in context.quotas):
        return []
    return context.run('mediaconvert', CHECKS, skip)
