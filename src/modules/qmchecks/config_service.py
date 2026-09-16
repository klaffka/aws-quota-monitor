"""AWS Config regional rule inventory."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [('L-0BE82991', 'AWS Config Rules per region',
           lambda ctx: dict(usage=len(ctx.call('config', 'describe_config_rules', 'ConfigRules')),
                            source='config:DescribeConfigRules', method='ACCOUNT_COUNT'))]


def get_current_quotastatus_config(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'config' for service, _ in context.quotas): return []
    return context.run('config', CHECKS, skip)
