"""AWS Resilience Hub application, assessment and recommendation quotas.

The import quotas count CloudFormation stacks, EKS clusters, namespaces and
Terraform state files offered to a single import call, the retention and size
quotas bound a document or a period, and the `ResilienceHubV2` quotas belong to
a service generation the SDK does not expose.
"""
from collections import Counter
from modules.qmcore.aws import CheckContext, NoData, maximum, session_from_env

RESILIENCEHUB = 'resiliencehub'
JOB_STATES = {'Pending', 'InProgress', 'Failed', 'Success'}
RUNNING_STATES = {'Pending', 'InProgress'}


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
]


def get_current_quotastatus_resiliencehub(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'resiliencehub' for service, _ in context.quotas):
        return []
    return context.run('resiliencehub', CHECKS, skip)
