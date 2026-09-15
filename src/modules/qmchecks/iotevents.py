"""AWS IoT Events alarm model inventory.

botocore no longer ships an `iotevents` client. The check still attempts the
call so it starts working again if the SDK restores the service, but reports
the absence as unsupported rather than failing the collector every run.
"""
from modules.qmcore.aws import CheckContext, sdk_call, session_from_env

IOTEVENTS = 'iotevents'


def alarm_models(ctx):
    models = sdk_call(ctx, IOTEVENTS, 'list_alarm_models', 'alarmModelSummaries')
    return dict(usage=len(models), source='iotevents:ListAlarmModels',
                method='ACCOUNT_COUNT')


CHECKS = [('L-134442DD', 'Maximum alarm models per account', alarm_models)]


def get_current_quotastatus_iotevents(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'iotevents' for service, _ in context.quotas):
        return []
    return context.run('iotevents', CHECKS, skip)
