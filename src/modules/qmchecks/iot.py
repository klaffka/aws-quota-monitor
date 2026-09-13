"""AWS IoT Core dynamic thing-group inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-2F036C7C', 'Maximum number of dynamic groups',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_thing_groups', 'thingGroups',
                                                thingGroupType='DYNAMIC')),
                            source='iot:ListThingGroups', method='ACCOUNT_COUNT')),
          ('L-B2C87795', 'Maximum number of job templates',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_job_templates', 'jobTemplates')),
                            source='iot:ListJobTemplates', method='ACCOUNT_COUNT')),
          ('L-0D30EFBA', 'Scheduled audits',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_scheduled_audits', 'scheduledAudits')),
                            source='iot:ListScheduledAudits', method='ACCOUNT_COUNT')),
          ('L-1A084077', 'Mitigation actions',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_mitigation_actions', 'actionIdentifiers')),
                            source='iot:ListMitigationActions', method='ACCOUNT_COUNT')),
          ('L-53A90E98', 'Custom metrics',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_custom_metrics', 'metricNames')),
                            source='iot:ListCustomMetrics', method='ACCOUNT_COUNT')),
          ('L-4C271B57', 'Streams per account',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_streams', 'streams')),
                            source='iot:ListStreams', method='ACCOUNT_COUNT')),
          ('L-A5B47E14', 'Maximum number of fleet metrics',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_fleet_metrics', 'fleetMetrics')),
                            source='iot:ListFleetMetrics', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_iot(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iot' for service, _ in context.quotas): return []
    return context.run('iot', CHECKS, skip)
