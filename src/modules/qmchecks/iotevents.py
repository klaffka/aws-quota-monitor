"""AWS IoT Events regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-134442DD', 'Maximum alarm models per account',
     lambda c: dict(usage=len(c.call('iotevents', 'list_alarm_models', 'alarmModelSummaries')),
                    source='iotevents:ListAlarmModels', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_iotevents(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotevents' for service, _ in context.quotas):
        return []
    return context.run('iotevents', CHECKS, skip)
