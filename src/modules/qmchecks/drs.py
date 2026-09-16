"""AWS Elastic Disaster Recovery source server, job and launch quotas."""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

DRS = 'drs'
JOB_STATES = {'PENDING', 'STARTED', 'COMPLETED'}
RUNNING_JOB_STATES = {'PENDING', 'STARTED'}
REPLICATION_STATES = {
    'STOPPED', 'INITIATING', 'INITIAL_SYNC', 'BACKLOG', 'CREATING_SNAPSHOT',
    'CONTINUOUS', 'PAUSED', 'RESCAN', 'STALLED', 'DISCONNECTED',
}
# A paused or stalled server still holds its staging area, so only a stopped or
# disconnected server is counted as no longer replicating.
IDLE_REPLICATION_STATES = {'STOPPED', 'DISCONNECTED'}


def source_servers(ctx):
    found = {}
    for server in ctx.call(DRS, 'describe_source_servers', 'items'):
        identity = server.get('sourceServerID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Source server is missing its identity')
        found[identity] = server
    return found


def replicating_source_servers(ctx):
    usage = 0
    for server in source_servers(ctx).values():
        state = (server.get('dataReplicationInfo') or {}).get('dataReplicationState')
        if state is None:
            continue
        if state not in REPLICATION_STATES:
            raise NoData('Source server has an unknown replication state')
        usage += state not in IDLE_REPLICATION_STATES
    return dict(usage=usage, source='drs:DescribeSourceServers',
                method='ACCOUNT_COUNT')


def jobs(ctx):
    found = {}
    for job in ctx.call(DRS, 'describe_jobs', 'items'):
        identity = job.get('jobID')
        if not isinstance(identity, str) or not identity:
            raise NoData('Recovery job is missing its identity')
        if job.get('status') not in JOB_STATES:
            raise NoData('Recovery job has an unknown status')
        found[identity] = job
    return found


def running_jobs(ctx):
    return {identity: job for identity, job in jobs(ctx).items()
            if job['status'] in RUNNING_JOB_STATES}


def _participants(job):
    servers = job.get('participatingServers') or []
    if not isinstance(servers, list):
        raise NoData('Recovery job has an invalid participant list')
    result = []
    for server in servers:
        identity = server.get('sourceServerID') if isinstance(server, dict) else None
        if not isinstance(identity, str) or not identity:
            raise NoData('Recovery job participant has no source server')
        result.append(identity)
    return result


def servers_in_a_single_job(ctx):
    values = [(identity, len(_participants(job)), None)
              for identity, job in running_jobs(ctx).items()]
    return maximum(values, 'DRSJob', 'drs:DescribeJobs')


def servers_in_all_jobs(ctx):
    usage = sum(len(_participants(job)) for job in running_jobs(ctx).values())
    return dict(usage=usage, source='drs:DescribeJobs', method='ACCOUNT_COUNT')


def jobs_per_source_server(ctx):
    counts = Counter({identity: 0 for identity in source_servers(ctx)})
    for job in running_jobs(ctx).values():
        for identity in _participants(job):
            counts[identity] += 1
    return maximum(((identity, count, None) for identity, count in counts.items()),
                   'DRSSourceServer', 'drs:DescribeJobs')


def launch_actions_per_resource(ctx):
    values = []
    for identity in source_servers(ctx):
        actions = ctx.call(DRS, 'list_launch_actions', 'items', resourceId=identity)
        for action in actions:
            if not isinstance(action.get('actionId'), str):
                raise NoData('Launch action is missing its identity')
        values.append((identity, len(actions), None))
    return maximum(values, 'DRSSourceServer', 'drs:ListLaunchActions')


CHECKS = [
    ('L-E28BE5E0', 'Max Total source servers Per AWS Account',
     lambda ctx: dict(usage=len(source_servers(ctx)),
                      source='drs:DescribeSourceServers', method='ACCOUNT_COUNT')),
    ('L-C1D14A2B', 'Max Total replicating source servers Per AWS Account',
     replicating_source_servers),
    ('L-D88FAC3A', 'Concurrent jobs in progress',
     lambda ctx: dict(usage=len(running_jobs(ctx)), source='drs:DescribeJobs',
                      method='ACCOUNT_COUNT')),
    ('L-DD6D028C', 'Max concurrent Jobs per source server', jobs_per_source_server),
    ('L-B827C881', 'Max source servers in a single Job', servers_in_a_single_job),
    ('L-05AFA8C6', 'Max source servers in all Jobs', servers_in_all_jobs),
    ('L-1F3FAE4D', 'Max number of launch configuration templates per AWS account',
     lambda ctx: dict(usage=len(ctx.call(DRS, 'describe_launch_configuration_templates',
                                         'items')),
                      source='drs:DescribeLaunchConfigurationTemplates',
                      method='ACCOUNT_COUNT')),
    ('L-4B0323BD', 'Max number of source networks per AWS account',
     lambda ctx: dict(usage=len(ctx.call(DRS, 'describe_source_networks', 'items')),
                      source='drs:DescribeSourceNetworks', method='ACCOUNT_COUNT')),
    ('L-0588D03B', 'Max number of launch actions per resource',
     launch_actions_per_resource),
]


def get_current_quotastatus_drs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'drs' for service, _ in context.quotas):
        return []
    return context.run('drs', CHECKS, skip)
