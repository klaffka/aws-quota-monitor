"""Application Migration Service inventories, jobs and action limits.

Archived applications, waves and source servers keep their own quotas, so every
inventory is split on `isArchived` rather than counted as a whole.
"""
from collections import Counter

from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

MGN = 'mgn'
JOB_STATES = {'PENDING', 'STARTED', 'COMPLETED'}
RUNNING_JOB_STATES = {'PENDING', 'STARTED'}


def _archived(entry, subject):
    value = entry.get('isArchived')
    if not isinstance(value, bool):
        raise NoData(f'Application Migration Service {subject} has no archive flag')
    return value


def _inventory(method, subject, archived):
    def check(ctx):
        usage = sum(_archived(entry, subject) == archived
                    for entry in ctx.call(MGN, method, 'items'))
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return dict(usage=usage, source=f'mgn:{operation}', method='ACCOUNT_COUNT')
    return check


def source_servers(ctx):
    found = {}
    for server in ctx.call(MGN, 'describe_source_servers', 'items'):
        identity = server.get('sourceServerID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Application Migration Service source server has no ID')
        found[identity] = server
    return found


def all_source_servers(ctx):
    return dict(usage=len(source_servers(ctx)), source='mgn:DescribeSourceServers',
                method='ACCOUNT_COUNT')


def _grouped(items, field, subject):
    """Group children by the parent they name, ignoring the unassigned ones."""
    counts = Counter()
    for item in items:
        parent = item.get(field)
        if parent is None:
            continue
        if not isinstance(parent, str) or not parent:
            raise NoData(f'Application Migration Service {subject} has an invalid parent')
        counts[parent] += 1
    return counts


def servers_per_application(ctx):
    counts = _grouped(source_servers(ctx).values(), 'applicationID', 'source server')
    return maximum(((parent, count, None) for parent, count in counts.items()),
                   'MGNApplication', 'mgn:DescribeSourceServers')


def applications_per_wave(ctx):
    counts = _grouped(ctx.call(MGN, 'list_applications', 'items'), 'waveID',
                      'application')
    return maximum(((parent, count, None) for parent, count in counts.items()),
                   'MGNWave', 'mgn:ListApplications')


def jobs(ctx):
    """Return the jobs that still occupy capacity, with their servers."""
    found = []
    for job in ctx.call(MGN, 'describe_jobs', 'items'):
        status = job.get('status')
        if status not in JOB_STATES:
            raise NoData('Application Migration Service job has an unknown status')
        if status not in RUNNING_JOB_STATES:
            continue
        identity = job.get('jobID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Application Migration Service job has no ID')
        servers = job.get('participatingServers')
        if not isinstance(servers, list):
            raise NoData('Application Migration Service job has no server list')
        found.append((identity, servers))
    return found


def running_jobs(ctx):
    return dict(usage=len(jobs(ctx)), source='mgn:DescribeJobs',
                method='ACCOUNT_COUNT')


def servers_in_all_jobs(ctx):
    return dict(usage=sum(len(servers) for _, servers in jobs(ctx)),
                source='mgn:DescribeJobs', method='ACCOUNT_COUNT')


def servers_in_one_job(ctx):
    return maximum(((identity, len(servers), None) for identity, servers in jobs(ctx)),
                   'MGNJob', 'mgn:DescribeJobs')


def jobs_per_source_server(ctx):
    counts = Counter()
    for _, servers in jobs(ctx):
        for server in servers:
            identity = server.get('sourceServerID')
            if not isinstance(identity, str) or not identity:
                raise NoData('Application Migration Service job names a server without an ID')
            counts[identity] += 1
    return maximum(((identity, count, None) for identity, count in counts.items()),
                   'MGNSourceServer', 'mgn:DescribeJobs')


def actions_per_source_server(ctx):
    values = [(identity, len(ctx.call(MGN, 'list_source_server_actions', 'items',
                                      sourceServerID=identity)), None)
              for identity in source_servers(ctx)]
    return maximum(values, 'MGNSourceServer',
                   'mgn:DescribeSourceServers+ListSourceServerActions')


def actions_per_template(ctx):
    values = []
    for template in ctx.call(MGN, 'describe_launch_configuration_templates', 'items'):
        identity = template.get('launchConfigurationTemplateID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Application Migration Service launch template has no ID')
        actions = ctx.call(MGN, 'list_template_actions', 'items',
                           launchConfigurationTemplateID=identity)
        values.append((identity, len(actions), None))
    return maximum(values, 'MGNLaunchConfigurationTemplate',
                   'mgn:DescribeLaunchConfigurationTemplates+ListTemplateActions')


CHECKS = [
    ('L-D5507441', 'Max active applications',
     _inventory('list_applications', 'application', False)),
    ('L-391504A2', 'Max archived applications',
     _inventory('list_applications', 'application', True)),
    ('L-9FD6E875', 'Max active waves',
     _inventory('list_waves', 'wave', False)),
    ('L-BB9C7114', 'Max archived waves',
     _inventory('list_waves', 'wave', True)),
    ('L-967C958D', 'Max Total Source Servers Per AWS Account', all_source_servers),
    ('L-50980698', 'Max Non-Archived Source Servers',
     _inventory('describe_source_servers', 'source server', False)),
    ('L-90A3F9F5', 'Max source servers per application', servers_per_application),
    ('L-CBE9E36A', 'Max applications per wave', applications_per_wave),
    ('L-FE2EBE17', 'Concurrent jobs in progress', running_jobs),
    ('L-4FF77426', 'Max Source Servers in all Jobs', servers_in_all_jobs),
    ('L-F1FD732F', 'Max Source Servers in a single Job', servers_in_one_job),
    ('L-615F978B', 'Max concurrent Jobs per Source Server', jobs_per_source_server),
    ('L-0E532B45', 'Max actions per source server', actions_per_source_server),
    ('L-322CA331', 'Max actions per template', actions_per_template),
    ('L-D617A7E7', 'Max network migration definitions per account per Region',
     lambda ctx: dict(usage=len(ctx.call(MGN, 'list_network_migration_definitions',
                                         'items')),
                      source='mgn:ListNetworkMigrationDefinitions',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_mgn(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'mgn' for service, _ in context.quotas):
        return []
    return context.run('mgn', CHECKS, skip)
