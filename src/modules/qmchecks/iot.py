"""AWS IoT device management, security profile, job, command and stream quotas.

The wildcard and query term quotas bound a single query, the tunnel quotas bound
one tunnel, and the pre-signed URL and timer quotas name a period. The named
shadow and geo location filters are different: they configure the fleet index
for the whole account, so GetIndexingConfiguration reports them.

The job and job template length quotas bound a stored field rather than a
request, so each is the longest value the inventory holds. They ride the walks
`targets_per_job` and the job template count already make, and an optional
field that is absent is a length of nothing rather than a missing value.
`DocumentSource length` is the exception and stays open: it lives on the job
template detail, which nothing else fetches.

`Pre-signed URL lifetime` is a period rather than a length but follows the same
rule: the job stores it, so it is read back. A job whose document is inline
signs no URL and configures no lifetime, which is zero.
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


# A behaviour states its threshold in whichever of these the metric needs; the
# scalar members bound one value rather than a list of them.
VALUE_LISTS = ('cidrs', 'ports', 'numbers', 'strings')
# The states an execution can still leave, so both of them hold the quota.
COMMAND_RUNNING = ('CREATED', 'IN_PROGRESS')
# ListCommandExecutions needs a time filter; one opening at the epoch keeps
# every execution, however long its timeout.
COMMAND_EPOCH = {'after': '1970-01-01T00:00'}


def behaviour_value_elements(ctx):
    """The quota bounds one behaviour's list, not the profile's behaviours."""
    values = []
    for name in security_profiles(ctx):
        detail = ctx.call(IOT, 'describe_security_profile', securityProfileName=name)
        for behaviour in detail.get('behaviors') or []:
            behaviour_name = behaviour.get('name')
            if not isinstance(behaviour_name, str) or not behaviour_name:
                raise NoData('IoT security profile behaviour is missing its name')
            value = (behaviour.get('criteria') or {}).get('value') or {}
            if not isinstance(value, dict):
                raise NoData('IoT security profile behaviour has an invalid value')
            elements = sum(len(value.get(member) or ()) for member in VALUE_LISTS)
            values.append((f'{name}/{behaviour_name}', elements, None))
    return maximum(values, 'IoTSecurityProfileBehavior', 'iot:DescribeSecurityProfile')


def targets_per_job(ctx):
    """A job keeps its targets after it finishes, so every job still holds one."""
    values = []
    for job in ctx.call(IOT, 'list_jobs', 'jobs'):
        identity = job.get('jobId')
        if not isinstance(identity, str) or not identity:
            raise NoData('IoT job is missing its identity')
        detail = ctx.call(IOT, 'describe_job', jobId=identity).get('job') or {}
        if detail.get('jobId') != identity:
            raise NoData('IoT job detail has a different identity')
        values.append((identity, len(detail.get('targets') or ()), None))
    return maximum(values, 'IoTJob', 'iot:ListJobs+DescribeJob')


def index_filter(ctx, member):
    """Count one fleet index filter, which is configured per account."""
    configuration = ctx.call(IOT, 'get_indexing_configuration').get('thingIndexingConfiguration')
    if not isinstance(configuration, dict):
        raise NoData('IoT indexing configuration has no thingIndexingConfiguration')
    entries = (configuration.get('filter') or {}).get(member) or []
    if not isinstance(entries, list):
        raise NoData(f'IoT fleet index filter has an invalid {member} list')
    return dict(usage=len(entries), source='iot:GetIndexingConfiguration',
                method='ACCOUNT_COUNT')


def parameters_per_command(ctx):
    values = []
    for command in ctx.call(IOT, 'list_commands', 'commands'):
        identity = command.get('commandId')
        if not isinstance(identity, str) or not identity:
            raise NoData('IoT command is missing its identity')
        detail = ctx.call(IOT, 'get_command', commandId=identity)
        if detail.get('commandId') != identity:
            raise NoData('IoT command detail has a different identity')
        values.append((identity, len(detail.get('mandatoryParameters') or ()), None))
    return maximum(values, 'IoTCommand', 'iot:ListCommands+GetCommand')


def running_command_executions(ctx):
    """Walk each command's executions; IoT lists them only per command or device.

    A listing by command ARN refuses a status filter and requires a time filter,
    so every execution started since the epoch is read and the unfinished ones
    are counted here.
    """
    usage = 0
    for command in ctx.call(IOT, 'list_commands', 'commands'):
        arn = command.get('commandArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('IoT command is missing its ARN')
        for execution in ctx.call(IOT, 'list_command_executions', 'commandExecutions',
                                  commandArn=arn, startedTimeFilter=COMMAND_EPOCH):
            status = execution.get('status')
            if not isinstance(status, str) or not status:
                raise NoData('IoT command execution has no status')
            usage += status in COMMAND_RUNNING
    return dict(usage=usage, source='iot:ListCommands+ListCommandExecutions',
                method='ACCOUNT_COUNT')


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


def dynamic_thing_groups(ctx):
    """ListThingGroups cannot filter by kind; a dynamic group has a query."""
    usage = 0
    for group in ctx.call('iot', 'list_thing_groups', 'thingGroups'):
        name = group.get('groupName')
        if not isinstance(name, str) or not name:
            raise NoData('IoT thing group is missing its name')
        detail = ctx.call('iot', 'describe_thing_group', thingGroupName=name)
        if detail.get('thingGroupName') != name:
            raise NoData('IoT thing group detail has a different identity')
        usage += bool(detail.get('queryString'))
    return dict(usage=usage, source='iot:ListThingGroups+DescribeThingGroup',
                method='ACCOUNT_COUNT')


def index_custom_fields(ctx, section):
    """Count the custom fields configured for one fleet index.

    GetIndexingConfiguration returns the configuration whether or not indexing
    is enabled, and a disabled index simply has no custom fields.
    """
    configuration = ctx.call(IOT, 'get_indexing_configuration').get(section)
    if not isinstance(configuration, dict):
        raise NoData(f'IoT indexing configuration has no {section}')
    fields = configuration.get('customFields') or []
    if not isinstance(fields, list):
        raise NoData(f'IoT {section} has an invalid custom field list')
    return dict(usage=len(fields), source='iot:GetIndexingConfiguration',
                method='ACCOUNT_COUNT')


def percentiles_per_fleet_metric(ctx):
    """Only a percentile aggregation carries values; the others carry none."""
    values = []
    for metric in ctx.call(IOT, 'list_fleet_metrics', 'fleetMetrics'):
        name = metric.get('metricName')
        if not isinstance(name, str) or not name:
            raise NoData('IoT fleet metric is missing its name')
        detail = ctx.call(IOT, 'describe_fleet_metric', metricName=name)
        if detail.get('metricName') != name:
            raise NoData('IoT fleet metric detail has a different identity')
        aggregation = detail.get('aggregationType') or {}
        values.append((name, len(aggregation.get('values') or ()), None))
    return maximum(values, 'IoTFleetMetric', 'iot:ListFleetMetrics+DescribeFleetMetric')


def jobs(ctx):
    """Every job, finished or not; a job keeps its fields after it completes."""
    for job in ctx.call(IOT, 'list_jobs', 'jobs'):
        identity = job.get('jobId')
        if not isinstance(identity, str) or not identity:
            raise NoData('IoT job is missing its identity')
        yield identity


def job_id_length(ctx):
    return maximum([(identity, len(identity), None) for identity in jobs(ctx)],
                   'IoTJob', 'iot:ListJobs')


def job_field_length(field):
    def check(ctx):
        values = []
        for identity in jobs(ctx):
            detail = ctx.call(IOT, 'describe_job', jobId=identity).get('job') or {}
            values.append((identity, len(detail.get(field) or ''), None))
        return maximum(values, 'IoTJob', 'iot:DescribeJob')
    return check


def presigned_url_lifetime(ctx):
    values = []
    for identity in jobs(ctx):
        detail = ctx.call(IOT, 'describe_job', jobId=identity).get('job') or {}
        config = detail.get('presignedUrlConfig') or {}
        values.append((identity, config.get('expiresInSec') or 0, None))
    return maximum(values, 'IoTJob', 'iot:DescribeJob')


def job_template_field_length(field):
    """The template listing carries both the id and the description."""
    def check(ctx):
        values = []
        for template in ctx.call(IOT, 'list_job_templates', 'jobTemplates'):
            identity = template.get('jobTemplateId')
            if not isinstance(identity, str) or not identity:
                raise NoData('IoT job template is missing its identity')
            value = identity if field == 'jobTemplateId' else template.get(field) or ''
            values.append((identity, len(value), None))
        return maximum(values, 'IoTJobTemplate', 'iot:ListJobTemplates')
    return check


CHECKS = [('L-2F036C7C', 'Maximum number of dynamic groups', dynamic_thing_groups),
          ('L-AE68DCD9', 'Maximum number of custom fields in AWS things index',
           lambda ctx: index_custom_fields(ctx, 'thingIndexingConfiguration')),
          ('L-8B2A08E6', 'Maximum number of custom fields in AWS thing groups index',
           lambda ctx: index_custom_fields(ctx, 'thingGroupIndexingConfiguration')),
          ('L-24513B55', 'Maximum number of percentile values per fleet metric',
           percentiles_per_fleet_metric),
          ('L-B2C87795', 'Maximum number of job templates',
           lambda ctx: dict(usage=len(ctx.call('iot', 'list_job_templates', 'jobTemplates')),
                            source='iot:ListJobTemplates', method='ACCOUNT_COUNT')),
          ('L-FBBB476F', 'Pre-signed URL lifetime', presigned_url_lifetime),
          ('L-E41D2F60', 'JobId Length', job_id_length),
          ('L-3123807D', 'Comment length', job_field_length('comment')),
          ('L-94973834', 'Job description length', job_field_length('description')),
          ('L-3470FAF6', 'JobTemplateId Length',
           job_template_field_length('jobTemplateId')),
          ('L-CEAD881C', 'Job Template description length',
           job_template_field_length('description')),
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
           on_demand_audits_in_progress),
          ('L-971FA845', 'Behavior metric value elements for each security profile',
           behaviour_value_elements),
          ('L-9D1E0A0D', 'Job Targets', targets_per_job),
          ('L-57F7D467', 'Maximum number of names in the named shadow names filter',
           lambda ctx: index_filter(ctx, 'namedShadowNames')),
          ('L-7068DC7F', 'Maximum number of targets in the geo locations filter',
           lambda ctx: index_filter(ctx, 'geoLocations')),
          ('L-F570A784', 'Parameters per dynamic command', parameters_per_command),
          ('L-631C84B3', 'Command execution concurrency limit',
           running_command_executions)]


def get_current_quotastatus_iot(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iot' for service, _ in context.quotas): return []
    return context.run('iot', CHECKS, skip)
