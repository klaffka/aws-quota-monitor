"""AWS CodeBuild project, VPC and concurrent build quotas.

`Minimum period for build timeout in minutes` states a floor rather than a
ceiling, and the two `Concurrent request for information` quotas bound API
concurrency, which leaves no inventory behind.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

CODEBUILD = 'codebuild'
BUILD_STATES = {'SUCCEEDED', 'FAILED', 'FAULT', 'TIMED_OUT', 'IN_PROGRESS', 'STOPPED'}
BATCH = 100
# A build cannot outlive CodeBuild's eight-hour maximum timeout, so the running
# ones sit among the newest ids. The window is still bounded, and a running
# build in the last batch scanned raises NoData rather than undercounting.
SCANNED_BUILDS = 1000

SIZES = (('Small', 'BUILD_GENERAL1_SMALL'), ('Medium', 'BUILD_GENERAL1_MEDIUM'),
         ('Large', 'BUILD_GENERAL1_LARGE'), ('XLarge', 'BUILD_GENERAL1_XLARGE'),
         ('2XLarge', 'BUILD_GENERAL1_2XLARGE'))
LAMBDA_SIZES = (('1GB', 'BUILD_LAMBDA_1GB'), ('2GB', 'BUILD_LAMBDA_2GB'),
                ('4GB', 'BUILD_LAMBDA_4GB'), ('8GB', 'BUILD_LAMBDA_8GB'),
                ('10GB', 'BUILD_LAMBDA_10GB'))

# Each quota names one environment type and compute size combination.
ENVIRONMENTS = {
    'L-9D07B6EF': ('LINUX_CONTAINER', 'BUILD_GENERAL1_SMALL'),
    'L-2DC20C30': ('LINUX_CONTAINER', 'BUILD_GENERAL1_MEDIUM'),
    'L-4DDC4A99': ('LINUX_CONTAINER', 'BUILD_GENERAL1_LARGE'),
    'L-04E5CA62': ('LINUX_CONTAINER', 'BUILD_GENERAL1_XLARGE'),
    'L-0397D009': ('LINUX_CONTAINER', 'BUILD_GENERAL1_2XLARGE'),
    'L-5ED1D25B': ('ARM_CONTAINER', 'BUILD_GENERAL1_SMALL'),
    'L-DF544FF3': ('ARM_CONTAINER', 'BUILD_GENERAL1_MEDIUM'),
    'L-596BEAB4': ('ARM_CONTAINER', 'BUILD_GENERAL1_LARGE'),
    'L-8D06F3EA': ('ARM_CONTAINER', 'BUILD_GENERAL1_XLARGE'),
    'L-1E43FDE0': ('ARM_CONTAINER', 'BUILD_GENERAL1_2XLARGE'),
    'L-F1FE1B52': ('LINUX_GPU_CONTAINER', 'BUILD_GENERAL1_SMALL'),
    'L-D906BEE7': ('LINUX_GPU_CONTAINER', 'BUILD_GENERAL1_LARGE'),
    'L-0544DB6A': ('WINDOWS_SERVER_2022_CONTAINER', 'BUILD_GENERAL1_MEDIUM'),
    'L-C3D92D78': ('WINDOWS_SERVER_2022_CONTAINER', 'BUILD_GENERAL1_LARGE'),
    'L-0DED26C7': ('WINDOWS_SERVER_2022_CONTAINER', 'BUILD_GENERAL1_2XLARGE'),
    'L-F2D50796': ('WINDOWS_SERVER_2022_CONTAINER', 'BUILD_GENERAL1_XLARGE'),
    'L-03FBB1ED': ('LINUX_LAMBDA_CONTAINER', 'BUILD_LAMBDA_1GB'),
    'L-1DFDD5F9': ('LINUX_LAMBDA_CONTAINER', 'BUILD_LAMBDA_2GB'),
    'L-39DB2B0B': ('LINUX_LAMBDA_CONTAINER', 'BUILD_LAMBDA_4GB'),
    'L-049948E0': ('LINUX_LAMBDA_CONTAINER', 'BUILD_LAMBDA_8GB'),
    'L-E692F494': ('LINUX_LAMBDA_CONTAINER', 'BUILD_LAMBDA_10GB'),
    'L-FD92223D': ('ARM_LAMBDA_CONTAINER', 'BUILD_LAMBDA_1GB'),
    'L-DE99852F': ('ARM_LAMBDA_CONTAINER', 'BUILD_LAMBDA_2GB'),
    'L-72045165': ('ARM_LAMBDA_CONTAINER', 'BUILD_LAMBDA_4GB'),
    'L-546A802A': ('ARM_LAMBDA_CONTAINER', 'BUILD_LAMBDA_8GB'),
    'L-36AF3CA5': ('ARM_LAMBDA_CONTAINER', 'BUILD_LAMBDA_10GB'),
}

ENVIRONMENT_NAMES = {
    'LINUX_CONTAINER': 'Linux', 'ARM_CONTAINER': 'ARM',
    'LINUX_GPU_CONTAINER': 'Linux GPU',
    'WINDOWS_SERVER_2022_CONTAINER': 'Windows Server 2022',
    'LINUX_LAMBDA_CONTAINER': 'Linux Lambda', 'ARM_LAMBDA_CONTAINER': 'ARM Lambda',
}
SIZE_NAMES = dict((code, label) for label, code in SIZES + LAMBDA_SIZES)
# The GPU quotas spell their environment without the separator the others use.
QUOTA_NAMES = {
    'L-F1FE1B52': 'Concurrently running builds for Linux GPU Small environment',
    'L-D906BEE7': 'Concurrently running builds for Linux GPU Large environment',
}


def _quota_name(code, environment, compute):
    return QUOTA_NAMES.get(code, f'Concurrently running builds for '
                                 f'{ENVIRONMENT_NAMES[environment]}/'
                                 f'{SIZE_NAMES[compute]} environment')


def projects(ctx):
    found = []
    for name in ctx.call(CODEBUILD, 'list_projects', 'projects'):
        if not isinstance(name, str) or not name:
            raise NoData('CodeBuild project is missing its name')
        if name not in found:
            found.append(name)
    return found


def project_details(ctx):
    found = []
    names = projects(ctx)
    for offset in range(0, len(names), BATCH):
        batch = names[offset:offset + BATCH]
        response = ctx.call(CODEBUILD, 'batch_get_projects', names=batch)
        if response.get('projectsNotFound'):
            raise NoData('CodeBuild project disappeared while being read')
        found.extend(response.get('projects') or [])
    return found


def running_builds(ctx):
    """Count builds still in progress, grouped by environment and compute size."""
    identifiers = []
    for identity in ctx.call(CODEBUILD, 'list_builds', 'ids',
                             sortOrder='DESCENDING'):
        identifiers.append(identity)
        if len(identifiers) >= SCANNED_BUILDS:
            break
    counts = Counter()
    running_in_last_batch = False
    for offset in range(0, len(identifiers), BATCH):
        batch = identifiers[offset:offset + BATCH]
        running_in_last_batch = False
        for build in ctx.call(CODEBUILD, 'batch_get_builds', ids=batch).get('builds') or []:
            status = build.get('buildStatus')
            if status not in BUILD_STATES:
                raise NoData('CodeBuild build has an unknown status')
            if status != 'IN_PROGRESS':
                continue
            environment = build.get('environment') or {}
            key = (environment.get('type'), environment.get('computeType'))
            if not all(key):
                raise NoData('CodeBuild build has no environment')
            counts[key] += 1
            running_in_last_batch = True
    if running_in_last_batch and len(identifiers) >= SCANNED_BUILDS:
        raise NoData('CodeBuild running builds reach the end of the scanned window')
    return counts


def _concurrent_builds(environment, compute):
    def check(ctx):
        usage = running_builds(ctx)[(environment, compute)]
        return dict(usage=usage, source='codebuild:ListBuilds+BatchGetBuilds',
                    method='ACCOUNT_COUNT')
    return check


def _project_maximum(measure):
    def check(ctx):
        values = []
        for project in project_details(ctx):
            name = project.get('name')
            if not isinstance(name, str) or not name:
                raise NoData('CodeBuild project is missing its name')
            values.append((name, measure(project), None))
        return maximum(values, 'CodeBuildProject', 'codebuild:BatchGetProjects')
    return check


def _vpc_list(field):
    def measure(project):
        configuration = project.get('vpcConfig') or {}
        entries = configuration.get(field) or []
        if not isinstance(entries, list):
            raise NoData('CodeBuild project has an invalid VPC configuration')
        return len(entries)
    return measure


def _timeout(project):
    timeout = project.get('timeoutInMinutes')
    if timeout is None:
        return 0
    if not isinstance(timeout, int) or isinstance(timeout, bool):
        raise NoData('CodeBuild project has an invalid build timeout')
    return timeout


CHECKS = [
    ('L-ACCF6C0D', 'Build projects',
     lambda ctx: dict(usage=len(projects(ctx)), source='codebuild:ListProjects',
                      method='ACCOUNT_COUNT')),
    ('L-BECF4531', 'Associated tags per project',
     _project_maximum(lambda project: len(project.get('tags') or []))),
    ('L-EDB7A61A', 'Security groups under VPC configuration',
     _project_maximum(_vpc_list('securityGroupIds'))),
    ('L-33638FE6', 'Subnets under VPC configuration',
     _project_maximum(_vpc_list('subnets'))),
    ('L-4167E76F', 'Build timeout in minutes', _project_maximum(_timeout)),
    *[(code, _quota_name(code, environment, compute),
       _concurrent_builds(environment, compute))
      for code, (environment, compute) in ENVIRONMENTS.items()],
]


def get_current_quotastatus_codebuild(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'codebuild' for service, _ in context.quotas):
        return []
    return context.run('codebuild', CHECKS, skip)
