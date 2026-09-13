"""Amazon CloudWatch Application Signals SLO inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-3FECAFD0', 'Number of SLOs per Region',
     lambda ctx: dict(usage=len(ctx.call('application-signals',
                                        'list_service_level_objectives', 'SloSummaries')),
                      source='application-signals:ListServiceLevelObjectives',
                      method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_applicationsignals(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'application-signals' for service, _ in context.quotas):
        return []
    return context.run('application-signals', CHECKS, skip)
