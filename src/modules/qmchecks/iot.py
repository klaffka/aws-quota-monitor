"""AWS IoT device management, security profile, job and stream quotas.

The wildcard, query term, shadow name and tunnel quotas bound a single query or
tunnel, and the pre-signed URL and timer quotas name a period.
"""
from collections import Counter
from datetime import timedelta
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

IOT = 'iot'
# ListAuditTasks needs a window. An on-demand audit does not run for a week, so
# seven days covers every task that can still be in progress.
AUDIT_WINDOW = timedelta(days=7)
JOB_STATES = {'IN_PROGRESS', 'CANCELED', 'COMPLETED', 'DELETION_IN_PROGRESS',
              'SCHEDULED'}


def _count(method, key, source, **kwargs):
    return lambda ctx: dict(usage=len(ctx.call(IOT, method, key, **kwargs)),
                            source=source, method='ACCOUNT_COUNT')


def _running_jobs(target_selection=None):
    """IoT filters jobs server side, so ask only for the ones in progress."""
    def check(ctx):
        arguments = {'status': 'IN_PROGRESS'}
        if target_selection is not None:
            arguments['targetSelection'] = target_selection
        usage = 0
        for job in ctx.call(IOT, 'list_jobs', 'jobs', **arguments):
            status = job.get('status')
            if status is not None and status not in JOB_STATES:
                raise NoData('IoT job has an unknown status')
            usage += 1
        return dict(usage=usage, source='iot:ListJobs', method='ACCOUNT_COUNT')
    return check


def security_profiles(ctx):
    found = []
    for profile in ctx.call(IOT, 'list_security_profiles',
                            'securityProfileIdentifiers'):
        name = profile.get('name')
        if not isinstance(name, str) or not name:
            raise NoData('IoT security profile is missing its name')
        found.append(name)
    return found


def behaviors_per_security_profile(ctx):
    values = []
    for name in security_profiles(ctx):
        detail = ctx.call(IOT, 'describe_security_profile', securityProfileName=name)
        behaviors = detail.get('behaviors') or []
        if not isinstance(behaviors, list):
            raise NoData('IoT security profile has an invalid behavior list')
        values.append((name, len(behaviors), None))
    return maximum(values, 'IoTSecurityProfile', 'iot:DescribeSecurityProfile')


def security_profiles_per_target(ctx):
    """Invert the per-profile target listing, the only direction AWS offers."""
    counts = Counter()
    for name in security_profiles(ctx):
        for target in ctx.call(IOT, 'list_targets_for_security_profile',
                               'securityProfileTargets',
                               securityProfileName=name):
            arn = target.get('arn')
            if not isinstance(arn, str) or not arn:
                raise NoData('IoT security profile target has no ARN')
            counts[arn] += 1
    return maximum(((arn, count, None) for arn, count in counts.items()),
                   'IoTSecurityProfileTarget',
                   'iot:ListTargetsForSecurityProfile')


def on_demand_audits_in_progress(ctx):
    tasks = ctx.call(IOT, 'list_audit_tasks', 'tasks',
                     startTime=ctx.now - AUDIT_WINDOW, endTime=ctx.now,
                     taskStatus='IN_PROGRESS', taskType='ON_DEMAND_AUDIT_TASK')
    return dict(usage=len(tasks), source='iot:ListAuditTasks',
                method='ACCOUNT_COUNT')


def files_per_stream(ctx):
    values = []
    for stream in ctx.call(IOT, 'list_streams', 'streams'):
        identity = stream.get('streamId')
        if not isinstance(identity, str) or not identity:
            raise NoData('IoT stream is missing its identity')
        info = ctx.call(IOT, 'describe_stream', streamId=identity).get('streamInfo')
        if not isinstance(info, dict):
            raise NoData('IoT stream has no detail')
        files = info.get('files') or []
        if not isinstance(files, list):
            raise NoData('IoT stream has an invalid file list')
        values.append((identity, len(files), None))
    return maximum(values, 'IoTStream', 'iot:DescribeStream')


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
                            source='iot:ListFleetMetrics', method='ACCOUNT_COUNT')),
          ('L-FBF5CD89', 'Concurrent jobs', _running_jobs()),
          ('L-4E068A30', 'Active continuous jobs', _running_jobs('CONTINUOUS')),
          ('L-D80B05DB', 'Active snapshot jobs', _running_jobs('SNAPSHOT')),
          ('L-8B5F47E6', 'Metric dimensions',
           _count('list_dimensions', 'dimensionNames', 'iot:ListDimensions')),
          ('L-2F1C9734', 'Behaviors for each security profile',
           behaviors_per_security_profile),
          ('L-FF03CD81', 'Security profiles for each target',
           security_profiles_per_target),
          ('L-D32D434B', 'Files per stream', files_per_stream),
          ('L-1EF777B4', 'Simultaneous in progress on-demand audits',
           on_demand_audits_in_progress)]


def get_current_quotastatus_iot(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iot' for service, _ in context.quotas): return []
    return context.run('iot', CHECKS, skip)
