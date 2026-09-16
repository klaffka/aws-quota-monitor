"""AWS Resilience Hub application, assessment and recommendation quotas.

The import quotas count CloudFormation stacks, EKS clusters, namespaces and
Terraform state files offered to a single import call, and the retention and
size quotas bound a document or a period. The `ResilienceHubV2` quotas belong
to the second-generation service and are read through its own client, whose
status values are upper case where the first generation's are mixed case.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

RESILIENCEHUB = 'resiliencehub'
RESILIENCEHUBV2 = 'resiliencehubv2'
JOB_STATES = {'Pending', 'InProgress', 'Failed', 'Success'}
RUNNING_STATES = {'Pending', 'InProgress'}
V2_ASSESSMENT_STATES = {'NOT_STARTED', 'PENDING', 'IN_PROGRESS', 'FAILED', 'SUCCESS'}
V2_RUNNING_STATES = {'PENDING', 'IN_PROGRESS'}


def apps(ctx):
    found = []
    for app in ctx.call(RESILIENCEHUB, 'list_apps', 'appSummaries'):
        arn = app.get('appArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Resilience Hub application is missing its ARN')
        if arn not in found:
            found.append(arn)
    return found


def latest_version(app, ctx):
    """Use the newest application version, which the newer entries end with."""
    versions = ctx.call(RESILIENCEHUB, 'list_app_versions', 'appVersions', appArn=app)
    names = [version.get('appVersion') for version in versions]
    if not names or not all(isinstance(name, str) and name for name in names):
        raise NoData('Resilience Hub application has no version')
    return names[-1]


def _per_app_version(method, key, resource_type, source):
    def check(ctx):
        values = []
        for app in apps(ctx):
            entries = ctx.call(RESILIENCEHUB, method, key, appArn=app,
                               appVersion=latest_version(app, ctx))
            values.append((app, len(entries), None))
        return maximum(values, resource_type, source)
    return check


def _running(ctx, method, key, status_field):
    for item in ctx.call(RESILIENCEHUB, method, key):
        status = item.get(status_field)
        if status not in JOB_STATES:
            raise NoData('Resilience Hub job has an unknown status')
        if status in RUNNING_STATES:
            yield item


def _running_count(method, key, status_field, source):
    def check(ctx):
        usage = sum(1 for _ in _running(ctx, method, key, status_field))
        return dict(usage=usage, source=source, method='ACCOUNT_COUNT')
    return check


def _running_per_app(method, key, status_field, source):
    def check(ctx):
        counts = Counter({app: 0 for app in apps(ctx)})
        for item in _running(ctx, method, key, status_field):
            app = item.get('appArn')
            if not isinstance(app, str) or not app:
                raise NoData('Resilience Hub job names no application')
            counts[app] += 1
        return maximum(((app, count, None) for app, count in counts.items()),
                       'ResilienceHubApp', source)
    return check


def v2_services(ctx):
    """Return each second-generation service by ARN, with its summary."""
    found = {}
    for service in ctx.call(RESILIENCEHUBV2, 'list_services', 'serviceSummaries'):
        arn = service.get('serviceArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Resilience Hub service is missing its ARN')
        found[arn] = service
    return found


def v2_systems(ctx):
    found = {}
    for system in ctx.call(RESILIENCEHUBV2, 'list_systems', 'systemSummaries'):
        arn = system.get('systemArn')
        if not isinstance(arn, str) or not arn:
            raise NoData('Resilience Hub system is missing its ARN')
        found[arn] = system
    return found


def _v2_count(loader, source):
    return lambda ctx: dict(usage=len(loader(ctx)), source=source,
                            method='ACCOUNT_COUNT')


def _v2_summary_list(field):
    """Read a list the service summary already carries, without a further call."""
    def check(ctx):
        values = []
        for arn, service in v2_services(ctx).items():
            entries = service.get(field)
            if entries is None:
                continue
            if not isinstance(entries, list):
                raise NoData(f'Resilience Hub service has an invalid {field}')
            values.append((arn, len(entries), None))
        return maximum(values, 'ResilienceHubService', 'resiliencehubv2:ListServices')
    return check


def _v2_per_service(method, key, **arguments):
    def check(ctx):
        values = [(arn, len(ctx.call(RESILIENCEHUBV2, method, key, serviceArn=arn,
                                     **arguments)), None)
                  for arn in v2_services(ctx)]
        operation = ''.join(part.capitalize() for part in method.split('_'))
        return maximum(values, 'ResilienceHubService',
                       f'resiliencehubv2:{operation}')
    return check


def v2_running_assessments_per_service(ctx):
    values = []
    for arn in v2_services(ctx):
        usage = 0
        for assessment in ctx.call(RESILIENCEHUBV2, 'list_failure_mode_assessments',
                                   'assessmentSummaries', serviceArn=arn):
            status = assessment.get('assessmentStatus')
            if status is not None and status not in V2_ASSESSMENT_STATES:
                raise NoData('Resilience Hub assessment has an unknown status')
            usage += status in V2_RUNNING_STATES
        values.append((arn, usage, None))
    return maximum(values, 'ResilienceHubService',
                   'resiliencehubv2:ListFailureModeAssessments')


def v2_user_journeys_per_system(ctx):
    """The system summary counts its journeys, so no further call is needed."""
    values = []
    for arn, system in v2_systems(ctx).items():
        count = system.get('userJourneysCount')
        if count is None:
            continue
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise NoData('Resilience Hub system has an invalid journey count')
        values.append((arn, count, None))
    return maximum(values, 'ResilienceHubSystem', 'resiliencehubv2:ListSystems')


def v2_services_per_user_journey(ctx):
    values = []
    for system in v2_systems(ctx):
        for journey in ctx.call(RESILIENCEHUBV2, 'list_user_journeys',
                                'userJourneySummaries', systemArn=system):
            identity = journey.get('userJourneyId')
            if not isinstance(identity, str) or not identity:
                raise NoData('Resilience Hub user journey is missing its identity')
            services = ctx.call(RESILIENCEHUBV2, 'list_services', 'serviceSummaries',
                                systemArn=system, userJourneyId=identity)
            values.append((identity, len(services), None))
    return maximum(values, 'ResilienceHubUserJourney',
                   'resiliencehubv2:ListUserJourneys+ListServices')


def v2_tags_per_input_source(ctx):
    values = []
    for arn in v2_services(ctx):
        for source in ctx.call(RESILIENCEHUBV2, 'list_input_sources',
                               'inputSourceSummaries', serviceArn=arn):
            tags = source.get('resourceTags')
            if tags is None:
                continue
            if not isinstance(tags, list):
                raise NoData('Resilience Hub input source has invalid tags')
            values.append((source.get('inputSourceId'), len(tags), None))
    return maximum(values, 'ResilienceHubInputSource',
                   'resiliencehubv2:ListInputSources')


CHECKS = [
    ('L-CBE304D4', 'Number of applications',
     lambda ctx: dict(usage=len(apps(ctx)), source='resiliencehub:ListApps',
                      method='ACCOUNT_COUNT')),
    ('L-F9AC239A', 'Number of Resiliency Policies',
     lambda ctx: dict(usage=len(ctx.call(RESILIENCEHUB, 'list_resiliency_policies',
                                         'resiliencyPolicies')),
                      source='resiliencehub:ListResiliencyPolicies',
                      method='ACCOUNT_COUNT')),
    ('L-0076B5C6', 'Number of Application Components per application',
     _per_app_version('list_app_version_app_components', 'appComponents',
                      'ResilienceHubApp',
                      'resiliencehub:ListAppVersionAppComponents')),
    ('L-5EC6916A', 'Number of resources per application',
     _per_app_version('list_app_version_resources', 'physicalResources',
                      'ResilienceHubApp', 'resiliencehub:ListAppVersionResources')),
    ('L-BD955A74', 'Number of concurrent assessments per account',
     _running_count('list_app_assessments', 'assessmentSummaries', 'assessmentStatus',
                    'resiliencehub:ListAppAssessments')),
    ('L-0AD966B7', 'Number of concurrent assessments per application',
     _running_per_app('list_app_assessments', 'assessmentSummaries',
                      'assessmentStatus', 'resiliencehub:ListAppAssessments')),
    ('L-CB12CFEB', 'Number of concurrent recommendation templates per account',
     _running_count('list_recommendation_templates', 'recommendationTemplates',
                    'status', 'resiliencehub:ListRecommendationTemplates')),
    ('L-64AA3F12', 'Number of concurrent recommendation templates per application',
     _running_per_app('list_recommendation_templates', 'recommendationTemplates',
                      'status', 'resiliencehub:ListRecommendationTemplates')),
    ('L-FC254984', 'Number of ResilienceHubV2 services per account',
     _v2_count(v2_services, 'resiliencehubv2:ListServices')),
    ('L-6799E097', 'Number of ResilienceHubV2 systems per account',
     _v2_count(v2_systems, 'resiliencehubv2:ListSystems')),
    ('L-6F0E13A4', 'Number of ResilienceHubV2 policies per account',
     lambda ctx: dict(usage=len(ctx.call(RESILIENCEHUBV2, 'list_policies',
                                         'policySummaries')),
                      source='resiliencehubv2:ListPolicies',
                      method='ACCOUNT_COUNT')),
    ('L-358A975C', 'Number of ResilienceHubV2 systems per service',
     _v2_summary_list('associatedSystems')),
    ('L-3C215170', 'Number of ResilienceHubV2 regions per service',
     _v2_summary_list('regions')),
    ('L-2652C3BC', 'Number of ResilienceHubV2 resources per service',
     _v2_per_service('list_resources', 'serviceResources')),
    ('L-985E582D', 'Number of ResilienceHubV2 input sources per service',
     _v2_per_service('list_input_sources', 'inputSourceSummaries')),
    ('L-04157D7A', 'Number of ResilienceHubV2 service functions per service',
     _v2_per_service('list_service_functions', 'serviceFunctions')),
    ('L-FCCEDB4B', 'Number of ResilienceHubV2 concurrent assessments per service',
     v2_running_assessments_per_service),
    ('L-EB92175D', 'Number of ResilienceHubV2 user journeys per system',
     v2_user_journeys_per_system),
    ('L-ED7E6FFD', 'Number of ResilienceHubV2 services per user journey',
     v2_services_per_user_journey),
    ('L-04E7C378', 'Number of ResilienceHubV2 tags per input source',
     v2_tags_per_input_source),
]


def get_current_quotastatus_resiliencehub(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'resiliencehub' for service, _ in context.quotas):
        return []
    return context.run('resiliencehub', CHECKS, skip)
