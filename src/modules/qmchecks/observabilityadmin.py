"""CloudWatch observability admin centralization rule quota.

The three pipeline quotas separate pipelines by source kind, which the pipeline
summary reports only as an undocumented `Source.Type` string, and the logs
centralization throughput quota is a rate.
"""
from modules.qmcore.aws import CheckContext, NoData, session_from_env

ADMIN = 'observabilityadmin'


def organization_centralization_rules(ctx):
    found = set()
    for rule in ctx.call(ADMIN, 'list_centralization_rules_for_organization',
                         'CentralizationRuleSummaries'):
        name = rule.get('RuleName')
        if not isinstance(name, str) or not name:
            raise NoData('Centralization rule is missing its name')
        found.add(name)
    return dict(usage=len(found),
                source='observabilityadmin:ListCentralizationRulesForOrganization',
                method='ACCOUNT_COUNT')


CHECKS = [('L-B8EC8109', 'Organization Centralization Rules',
           organization_centralization_rules)]


def get_current_quotastatus_observabilityadmin(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'observabilityadmin' for service, _ in context.quotas):
        return []
    return context.run('observabilityadmin', CHECKS, skip)
