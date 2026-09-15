"""AWS Snow Family device quotas, counted from the jobs that hold a device."""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

SNOWBALL = 'snowball'
JOB_STATES = {'New', 'PreparingAppliance', 'PreparingShipment', 'InTransitToCustomer',
              'WithCustomer', 'InTransitToAWS', 'WithAWSSortingFacility', 'WithAWS',
              'InProgress', 'Complete', 'Cancelled', 'Listing', 'Pending'}
# A complete or cancelled job has released its device.
RELEASED_STATES = {'Complete', 'Cancelled'}
SNOWBALL_TYPES = {'STANDARD', 'EDGE', 'EDGE_C', 'EDGE_CG', 'EDGE_S', 'SNC1_HDD',
                  'SNC1_SSD', 'V3_5C', 'V3_5S', 'RACK_5U_C'}
EDGE_TYPES = {'EDGE', 'EDGE_C', 'EDGE_CG', 'EDGE_S', 'V3_5C', 'V3_5S', 'RACK_5U_C'}
SNOWCONE_TYPES = {'SNC1_HDD', 'SNC1_SSD'}


def jobs(ctx):
    found = {}
    for job in ctx.call(SNOWBALL, 'list_jobs', 'JobListEntries'):
        identity = job.get('JobId')
        if not isinstance(identity, str) or not identity:
            raise NoData('Snow job is missing its identity')
        if job.get('JobState') not in JOB_STATES:
            raise NoData('Snow job has an unknown state')
        if job.get('SnowballType') not in SNOWBALL_TYPES:
            raise NoData('Snow job has an unknown device type')
        found[identity] = job
    return found


def _devices(types):
    def check(ctx):
        usage = sum(job['SnowballType'] in types
                    and job['JobState'] not in RELEASED_STATES
                    for job in jobs(ctx).values())
        return dict(usage=usage, source='snowball:ListJobs', method='ACCOUNT_COUNT')
    return check


CHECKS = [
    ('L-B6883B9F', 'Snowball Edge devices', _devices(EDGE_TYPES)),
    ('L-9F53AA61', 'Snowcone devices', _devices(SNOWCONE_TYPES)),
]


def get_current_quotastatus_snowball(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'snowball' for service, _ in context.quotas):
        return []
    return context.run('snowball', CHECKS, skip)
