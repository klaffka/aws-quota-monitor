"""Amazon Comprehend endpoint inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-55642075', 'Endpoints max active endpoints',
           lambda ctx: dict(usage=len(ctx.call('comprehend', 'list_endpoints', 'EndpointPropertiesList')),
                            source='comprehend:ListEndpoints', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_comprehend(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'comprehend' for service, _ in context.quotas): return []
    return context.run('comprehend', CHECKS, skip)
