"""Amazon MSK Connect regional custom-plugin counts."""
from modules.qmcore.aws import CheckContext, session_from_env

CHECKS = [
    ('L-F71212B3', 'Maximum custom plugins',
     lambda c: dict(usage=len(c.call('kafkaconnect', 'list_custom_plugins', 'customPlugins')),
                    source='kafkaconnect:ListCustomPlugins', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_kafkaconnect(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'kafkaconnect' for service, _ in context.quotas):
        return []
    return context.run('kafkaconnect', CHECKS, skip)
