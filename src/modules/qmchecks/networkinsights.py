"""Network Access Analyzer and Reachability Analyzer quota usage."""
from functools import partial

from modules.qmcore.aws import CheckContext, NoData, session_from_env


SERVICE = 'networkinsights'
STATUSES = {'running', 'succeeded', 'failed'}


def inventory(ctx, method, key, identity_field, subject):
    unique = {}
    for item in ctx.call('ec2', method, key):
        if not isinstance(item, dict):
            raise NoData(f'Network Insights {subject} inventory contains an invalid item')
        identity = item.get(identity_field)
        if not isinstance(identity, str) or not identity:
            raise NoData(f'Network Insights {subject} is missing {identity_field}')
        if identity in unique and unique[identity] != item:
            raise NoData(f'Network Insights {subject} inventory changed during pagination')
        unique[identity] = item
    return [unique[key] for key in sorted(unique)]


def account_count(ctx, method, key, identity_field, subject):
    items = inventory(ctx, method, key, identity_field, subject)
    return dict(usage=len(items), source=f'ec2:{method}', method='ACCOUNT_COUNT')


def concurrent_count(ctx, method, key, identity_field, subject):
    items = inventory(ctx, method, key, identity_field, subject)
    for item in items:
        if item.get('Status') not in STATUSES:
            raise NoData(f'Network Insights {subject} has an unknown status')
    return dict(usage=sum(item['Status'] == 'running' for item in items),
                source=f'ec2:{method}', method='ACCOUNT_COUNT')


ACCESS_SCOPE_ANALYSES = dict(
    method='describe_network_insights_access_scope_analyses',
    key='NetworkInsightsAccessScopeAnalyses',
    identity_field='NetworkInsightsAccessScopeAnalysisId',
    subject='access-scope analysis',
)
REACHABILITY_ANALYSES = dict(
    method='describe_network_insights_analyses',
    key='NetworkInsightsAnalyses',
    identity_field='NetworkInsightsAnalysisId',
    subject='reachability analysis',
)


CHECKS = [
    ('L-06B98CB1', 'Network Access Analyzer Access Scope Analyses',
     partial(account_count, **ACCESS_SCOPE_ANALYSES)),
    ('L-2AC9F231', 'Network Access Analyzer Concurrent Access Scope Analyses',
     partial(concurrent_count, **ACCESS_SCOPE_ANALYSES)),
    ('L-44B7545B', 'Reachability Analyzer Analyses',
     partial(account_count, **REACHABILITY_ANALYSES)),
    ('L-51CB2D5B', 'Reachability Analyzer Paths',
     partial(account_count, method='describe_network_insights_paths',
             key='NetworkInsightsPaths', identity_field='NetworkInsightsPathId',
             subject='reachability path')),
    ('L-72DF2E0E', 'Network Access Analyzer Access Scopes',
     partial(account_count, method='describe_network_insights_access_scopes',
             key='NetworkInsightsAccessScopes',
             identity_field='NetworkInsightsAccessScopeId', subject='access scope')),
    ('L-B393345A', 'Reachability Analyzer concurrent Analyses',
     partial(concurrent_count, **REACHABILITY_ANALYSES)),
]


def get_current_quotastatus_networkinsights(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == SERVICE for service, _ in context.quotas):
        return []
    return context.run(SERVICE, CHECKS, skip)
